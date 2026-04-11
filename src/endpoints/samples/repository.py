from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.endpoints.samples.model import Sample, SampleFile, SampleResult
from src.endpoints.samples.schema import SampleCreate

def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Sample]:
  return db.query(Sample).offset(skip).limit(limit).all()

def get_by_code(db: Session, code: str) -> dict | None:
  """Busca uma amostra pelo código e retorna junto com a URL da primeira imagem vinculada."""
  result = (
    db.query(Sample, SampleFile)
    .outerjoin(SampleFile, SampleFile.sample_id == Sample.id)
    .filter(Sample.code == code)
    .order_by(SampleFile.uploaded_at.asc())
    .first()
  )

  if result is None:
    return None

  sample, sample_file = result

  file_url = None
  file_name = None
  if sample_file:
    # storage_path é relativo à pasta uploads/ (ex: "amostras/foto.jpg")
    file_url = f"/uploads/{sample_file.storage_path}"
    file_name = sample_file.file_name

  return {
    "id": sample.id,
    "code": sample.code,
    "status": sample.status,
    "tier": sample.tier,
    "tier_label": sample.tier_label,
    "created_by": sample.created_by,
    "analyzed_by": sample.analyzed_by,
    "collected_at": sample.collected_at,
    "analyzed_at": sample.analyzed_at,
    "created_at": sample.created_at,
    "file_url": file_url,
    "file_name": file_name,
  }

def create(db: Session, data: SampleCreate) -> Sample:
  now = datetime.now(timezone.utc)
  new_sample = Sample(
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
  # Pegamos a data atual em formato string YYYY-MM-DD para garantir compatibilidade com func.date
  today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
  
  processed_samples = db.query(Sample).filter(Sample.status == "concluido").count()
  
  avg_conf = db.query(func.avg(SampleResult.confidence_score)).scalar() or 0.0
  confidence_percentage = round(avg_conf * 100, 1)

  anomalies = db.query(SampleResult).filter(SampleResult.confidence_score < 0.8).count()
  avg_time = 1.2
  
  # Estatísticas diárias
  daily_reads = db.query(Sample).filter(func.date(Sample.created_at) == today_str).count()
  daily_rejections = db.query(Sample).filter(
      func.date(Sample.created_at) == today_str,
      Sample.status == "rejeitado"
  ).count()

  recent_query = db.query(Sample, SampleResult).outerjoin(SampleResult, Sample.id == SampleResult.sample_id).order_by(Sample.created_at.desc()).limit(10).all()

  recent_samples = []
  for sample, result in recent_query:
      confidence = int(result.confidence_score * 100) if result else 0
      
      prediction = "Análise Pendente"
      if result:
          prediction = "Anomalia Detectada" if result.confidence_score < 0.8 else "Normal"
          if result.ml_raw_output and "predicted_class" in result.ml_raw_output:
              prediction = result.ml_raw_output["predicted_class"]

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

