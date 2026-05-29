from datetime import datetime, timezone, timedelta, date as date_type
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.endpoints.samples.model import Sample, SampleResult, Batch
from src.endpoints.samples.schema import SampleCreate, RaspSampleCreate

# Fuso horário do Brasil (UTC-3)
BRAZIL_TZ = timezone(timedelta(hours=-3))

RASP_USER_ID = 5

TIER_MAP = {
  "bom":     (1, "bom"),
  "ruim":    (2, "ruim"),
  "pessimo": (3, "pessimo"),
}

def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Sample]:
  return db.query(Sample).offset(skip).limit(limit).all()

def get_by_code(db: Session, code: str) -> dict | None:
  result = (
    db.query(Sample, SampleResult)
    .outerjoin(SampleResult, SampleResult.sample_id == Sample.id)
    .filter(Sample.code == code)
    .first()
  )

  if result is None:
    return None

  sample, sample_result = result

  image_url = None
  if sample_result and sample_result.image_path:
    p = sample_result.image_path
    image_url = p if p.startswith("http") else f"/uploads/{p}"

  prediction = None
  if sample_result and sample_result.ml_raw_output:
    prediction = sample_result.ml_raw_output.get("predicted_class")

  return {
    "id": sample.id,
    "batch_id": sample.batch_id,
    "code": sample.code,
    "status": sample.status,
    "tier": sample.tier,
    "tier_label": sample.tier_label,
    "created_by": sample.created_by,
    "collected_at": sample.collected_at,
    "analyzed_at": sample.analyzed_at,
    "created_at": sample.created_at,
    "image_url": image_url,
    "confidence_score": sample_result.confidence_score if sample_result else None,
    "prediction": prediction,
    "model_version": sample_result.model_version if sample_result else None,
  }

def create(db: Session, data: SampleCreate) -> Sample:
  now = datetime.now(timezone.utc)
  new_sample = Sample(
    batch_id=data.batch_id,
    code=data.code,
    created_by=data.created_by,
    collected_at=data.collected_at,
    tier_label=data.tier_label,
    created_at=now,
    status="pendente"
  )
  db.add(new_sample)
  db.commit()
  db.refresh(new_sample)
  return new_sample

def get_dashboard_data(db: Session) -> dict:
  today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')

  processed_samples = db.query(Sample).filter(Sample.status == "concluido").count()

  avg_conf = db.query(func.avg(SampleResult.confidence_score)).scalar() or 0.0
  confidence_percentage = round(avg_conf * 100, 1)

  anomalies = db.query(SampleResult).filter(
    SampleResult.confidence_score != None,
    SampleResult.confidence_score < 0.8,
  ).count()
  avg_time = 1.2

  daily_reads = db.query(Sample).filter(func.date(Sample.created_at) == today_str).count()
  daily_rejections = db.query(Sample).filter(
      func.date(Sample.created_at) == today_str,
      Sample.status == "rejeitado"
  ).count()

  # Leituras de ontem (para tendência)
  yesterday_str = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
  yesterday_reads = db.query(Sample).filter(func.date(Sample.created_at) == yesterday_str).count()

  # Contagem por tier (total histórico)
  tier_bom     = db.query(Sample).filter(Sample.tier == 1).count()
  tier_ruim    = db.query(Sample).filter(Sample.tier == 2).count()
  tier_pessimo = db.query(Sample).filter(Sample.tier == 3).count()

  # Turno e lote ativo
  now_local  = datetime.now(BRAZIL_TZ)
  hour_local = now_local.hour
  if 6 <= hour_local < 18:
    shift, current_shift = "D", "Diurno"
    shift_date = now_local.strftime("%Y%m%d")
  else:
    shift, current_shift = "N", "Noturno"
    shift_date = (now_local - timedelta(days=1)).strftime("%Y%m%d") if 0 <= hour_local < 6 else now_local.strftime("%Y%m%d")
  current_batch = f"RASP-{shift_date}-{shift}"

  recent_query = (
    db.query(Sample, SampleResult)
    .outerjoin(SampleResult, Sample.id == SampleResult.sample_id)
    .order_by(Sample.created_at.desc())
    .limit(10)
    .all()
  )

  recent_samples = []
  for sample, result in recent_query:
      prediction = "Análise Pendente"
      doctor = "—"
      if result and result.ml_raw_output:
          prediction = result.ml_raw_output.get("predicted_class", "Análise Pendente")
          doctor = result.ml_raw_output.get("doctor") or "—"

      sample_type = sample.tier_label or "Análise Padrão"

      status_class = "status-processing"
      if sample.status == "concluido":
          status_class = "status-completed"
      elif sample.status == "rejeitado":
          status_class = "status-flagged"

      recent_samples.append({
          "id": sample.code,
          "type": sample_type,
          "typeClass": "badge-blood",
          "patient": f"PT-{sample.created_by}",
          "prediction": prediction,
          "doctor": doctor,
          "confidence": 0,
          "status": sample.status.capitalize(),
          "statusClass": status_class
      })

  return {
      "stats": {
          "processed_samples": processed_samples,
          "confidence_score": confidence_percentage,
          "anomalies_detected": anomalies,
          "avg_processing_time": avg_time,
          "daily_reads": daily_reads,
          "daily_rejections": daily_rejections,
          "tier_bom": tier_bom,
          "tier_ruim": tier_ruim,
          "tier_pessimo": tier_pessimo,
          "yesterday_reads": yesterday_reads,
          "current_batch": current_batch,
          "current_shift": current_shift,
      },
      "recent_samples": recent_samples
  }

def get_or_create_daily_batch(db: Session) -> Batch:
  """
  Cria/retorna o lote do turno atual:
    Diurno  (D): 06:00–17:59 (horário Brasil UTC-3)
    Noturno (N): 18:00–05:59 (horário Brasil UTC-3)
  """
  now_local = datetime.now(BRAZIL_TZ)
  hour = now_local.hour

  if 6 <= hour < 18:
    shift = "D"
    date_str = now_local.strftime("%Y%m%d")
  else:
    shift = "N"
    # 00:00-05:59 local → ainda é turno noturno que começou ontem
    if 0 <= hour < 6:
      date_str = (now_local - timedelta(days=1)).strftime("%Y%m%d")
    else:
      date_str = now_local.strftime("%Y%m%d")

  code = f"RASP-{date_str}-{shift}"
  batch = db.query(Batch).filter(Batch.code == code).first()
  if not batch:
    batch = Batch(user_id=RASP_USER_ID, code=code, created_at=datetime.now(timezone.utc))
    db.add(batch)
    db.commit()
    db.refresh(batch)
  return batch

def _generate_sample_code(db: Session) -> str:
  year = datetime.now(timezone.utc).year
  prefix = f"SMP-{year}-"
  count = db.query(Sample).filter(Sample.code.like(f"{prefix}%")).count()
  return f"{prefix}{count + 1:03d}"

def create_rasp_sample(db: Session, data: RaspSampleCreate) -> Sample:
  tier_num, tier_label = TIER_MAP.get(data.tier, (None, data.tier))
  batch = get_or_create_daily_batch(db)
  now = datetime.now(timezone.utc)

  sample = Sample(
    batch_id=batch.id,
    code=_generate_sample_code(db),
    created_by=RASP_USER_ID,
    tier=tier_num,
    tier_label=tier_label,
    status="concluido",
    analyzed_at=now,
    collected_at=data.collected_at,
    created_at=now,
  )
  db.add(sample)
  db.commit()
  db.refresh(sample)

  result = SampleResult(
    sample_id=sample.id,
    image_path=data.gcp_url,
    confidence_score=1.0,
    ml_raw_output={"predicted_class": tier_label, "doctor": data.doctor_name},
    model_version="operator-v1",
    processed_at=now,
  )
  db.add(result)
  db.commit()

  return sample

def get_gallery_data(db: Session) -> list[dict]:
  results = (
    db.query(Sample, SampleResult)
    .outerjoin(SampleResult, SampleResult.sample_id == Sample.id)
    .order_by(Sample.created_at.desc())
    .all()
  )
  gallery = []
  for sample, result in results:
    if not result:
      continue
    prediction = result.ml_raw_output.get("predicted_class") if result.ml_raw_output else None
    image_url = result.image_path if result.image_path.startswith("http") else f"/uploads/{result.image_path}"
    gallery.append({
      "id": sample.id,
      "code": sample.code,
      "tier": sample.tier,
      "tier_label": sample.tier_label,
      "status": sample.status,
      "confidence_score": result.confidence_score,
      "prediction": prediction,
      "image_url": image_url,
      "processed_at": result.processed_at,
    })
  return gallery

def get_rasp_status(db: Session) -> dict:
  from datetime import timezone as tz
  last = (
    db.query(Sample)
    .filter(Sample.created_by == RASP_USER_ID)
    .order_by(Sample.created_at.desc())
    .first()
  )
  if not last:
    return {"is_online": False, "last_seen": None, "minutes_ago": None}
  last_seen = last.created_at
  if last_seen.tzinfo is None:
    last_seen = last_seen.replace(tzinfo=tz.utc)
  minutes_ago = int((datetime.now(tz.utc) - last_seen).total_seconds() / 60)
  return {
    "is_online": minutes_ago <= 10,
    "last_seen": last_seen,
    "minutes_ago": minutes_ago,
  }

def get_recent_rasp_samples(db: Session, limit: int = 5) -> list[dict]:
  results = (
    db.query(Sample, SampleResult)
    .outerjoin(SampleResult, SampleResult.sample_id == Sample.id)
    .filter(Sample.created_by == RASP_USER_ID)
    .order_by(Sample.created_at.desc())
    .limit(limit)
    .all()
  )
  items = []
  for sample, result in results:
    image_url = None
    if result and result.image_path:
      p = result.image_path
      image_url = p if p.startswith("http") else f"/uploads/{p}"
    items.append({
      "code": sample.code,
      "tier_label": sample.tier_label,
      "tier": sample.tier,
      "image_url": image_url,
      "collected_at": sample.collected_at,
    })
  return items

def get_pending_count(db: Session) -> dict:
  processing = db.query(Sample).filter(Sample.status == "processando").count()
  pending    = db.query(Sample).filter(Sample.status == "pendente").count()
  return {"processing": processing, "pending": pending, "total": processing + pending}

def get_time_series(db: Session, days: int = 14) -> list[dict]:
  """Retorna contagem de amostras por dia nos últimos N dias, agrupadas por tier."""
  today = date_type.today()
  result = []
  for i in range(days - 1, -1, -1):
    d = today - timedelta(days=i)
    d_str = d.strftime('%Y-%m-%d')
    bom     = db.query(Sample).filter(func.date(Sample.created_at) == d_str, Sample.tier == 1).count()
    ruim    = db.query(Sample).filter(func.date(Sample.created_at) == d_str, Sample.tier == 2).count()
    pessimo = db.query(Sample).filter(func.date(Sample.created_at) == d_str, Sample.tier == 3).count()
    sem_tier = db.query(Sample).filter(func.date(Sample.created_at) == d_str, Sample.tier == None).count()
    result.append({
      "date": d_str,
      "total": bom + ruim + pessimo + sem_tier,
      "bom": bom,
      "ruim": ruim,
      "pessimo": pessimo,
    })
  return result

def get_rasp_log(db: Session, limit: int = 20) -> list[dict]:
  """Retorna os últimos N registros enviados pelo Raspberry Pi com detalhes."""
  results = (
    db.query(Sample, SampleResult)
    .outerjoin(SampleResult, SampleResult.sample_id == Sample.id)
    .filter(Sample.created_by == RASP_USER_ID)
    .order_by(Sample.created_at.desc())
    .limit(limit)
    .all()
  )
  items = []
  for sample, result in results:
    doctor = None
    if result and result.ml_raw_output:
      doctor = result.ml_raw_output.get("doctor")
    image_url = None
    if result and result.image_path:
      p = result.image_path
      image_url = p if p.startswith("http") else f"/uploads/{p}"
    items.append({
      "code": sample.code,
      "tier": sample.tier,
      "tier_label": sample.tier_label,
      "doctor": doctor,
      "image_url": image_url,
      "collected_at": sample.collected_at,
      "created_at": sample.created_at,
    })
  return items

def get_doctor_stats(db: Session) -> list[dict]:
  """Retorna contagem de amostras por médico, ordenado por volume."""
  rows = db.query(SampleResult.ml_raw_output).filter(SampleResult.ml_raw_output != None).all()
  counts: dict[str, int] = {}
  for (raw,) in rows:
    if raw:
      doc = raw.get("doctor")
      if doc and doc not in ("—", "", None):
        counts[doc] = counts.get(doc, 0) + 1
  return [{"doctor": k, "count": v} for k, v in sorted(counts.items(), key=lambda x: -x[1])]

TIER_INT_TO_LABEL = {1: "bom", 2: "ruim", 3: "pessimo"}

def update_tier(db: Session, code: str, tier: int) -> Sample | None:
  sample = db.query(Sample).filter(Sample.code == code).first()
  if not sample:
    return None
  sample.tier = tier
  sample.tier_label = TIER_INT_TO_LABEL.get(tier, str(tier))
  db.commit()
  db.refresh(sample)
  return sample

def delete_by_code(db: Session, code: str) -> bool:
  """Remove uma amostra e seu resultado associado pelo código."""
  sample = db.query(Sample).filter(Sample.code == code).first()
  if not sample:
    return False
  # Remove SampleResult primeiro (sem cascade automático)
  db.query(SampleResult).filter(SampleResult.sample_id == sample.id).delete()
  db.delete(sample)
  db.commit()
  return True
