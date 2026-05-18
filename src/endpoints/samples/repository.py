from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.endpoints.samples.model import Sample, SampleResult, Batch
from src.endpoints.samples.schema import SampleCreate, RaspSampleCreate

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

  anomalies = db.query(SampleResult).filter(SampleResult.confidence_score < 0.8).count()
  avg_time = 1.2

  daily_reads = db.query(Sample).filter(func.date(Sample.created_at) == today_str).count()
  daily_rejections = db.query(Sample).filter(
      func.date(Sample.created_at) == today_str,
      Sample.status == "rejeitado"
  ).count()

  recent_query = (
    db.query(Sample, SampleResult)
    .outerjoin(SampleResult, Sample.id == SampleResult.sample_id)
    .order_by(Sample.created_at.desc())
    .limit(10)
    .all()
  )

  recent_samples = []
  for sample, result in recent_query:
      confidence = int(result.confidence_score * 100) if (result and result.confidence_score is not None) else 0

      prediction = "Análise Pendente"
      if result:
          if result.ml_raw_output and "predicted_class" in result.ml_raw_output:
              prediction = result.ml_raw_output["predicted_class"]
          elif result.confidence_score is not None:
              prediction = "Anomalia Detectada" if result.confidence_score < 0.8 else "Normal"

      sample_type = sample.tier_label or "Análise Padrão"
      type_class = "badge-blood"
      if "Sangue" in sample_type or "Blood" in sample_type:
          type_class = "badge-blood"
      elif "Tecido" in sample_type or "Tissue" in sample_type or "Biópsia" in sample_type:
          type_class = "badge-tissue"
      elif "RM" in sample_type or "Scan" in sample_type:
          type_class = "badge-scan"

      status_class = "status-processing"
      if sample.status == "concluido":
          status_class = "status-completed"
      elif sample.status == "rejeitado":
          status_class = "status-flagged"
      elif result and result.confidence_score < 0.8:
          status_class = "status-flagged"

      recent_samples.append({
          "id": sample.code,
          "type": sample_type,
          "typeClass": type_class,
          "patient": f"PT-{sample.created_by}",
          "prediction": prediction,
          "confidence": confidence,
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
          "daily_rejections": daily_rejections
      },
      "recent_samples": recent_samples
  }

def get_or_create_daily_batch(db: Session) -> Batch:
  today = datetime.now(timezone.utc).strftime("%Y%m%d")
  code = f"RASP-{today}"
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
    ml_raw_output={"predicted_class": tier_label},
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
