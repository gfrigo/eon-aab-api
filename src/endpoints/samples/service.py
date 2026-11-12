from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.endpoints.samples.model import Sample
from src.endpoints.samples.schema import SampleCreate, RaspSampleCreate
from src.endpoints.samples import repository

def get_samples(db: Session, skip: int = 0, limit: int = 100) -> list[Sample]:
  return repository.get_all(db, skip, limit)

def create_sample(db: Session, data: SampleCreate) -> Sample:
  return repository.create(db, data)

def get_dashboard(db: Session) -> dict:
  return repository.get_dashboard_data(db)

def get_sample_by_code(db: Session, code: str) -> dict:
  result = repository.get_by_code(db, code)
  if result is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Amostra com código '{code}' não encontrada."
    )
  return result

def get_gallery(db: Session) -> list:
  return repository.get_gallery_data(db)

def get_rasp_status(db: Session) -> dict:
  return repository.get_rasp_status(db)

def get_pending_count(db: Session) -> dict:
  return repository.get_pending_count(db)

def create_rasp_sample(db: Session, data: RaspSampleCreate, device) -> Sample:
  return repository.create_rasp_sample(db, data, device)

def create_pending_rasp_sample(db: Session, photo_id: str, image_filename: str, image_bytes: bytes, collected_at, device, tier: int | None = None) -> Sample:
  return repository.create_pending_rasp_sample(db, photo_id, image_filename, image_bytes, collected_at, device, tier)

def get_sample_image(db: Session, code: str) -> bytes:
  image = repository.get_sample_image(db, code)
  if image is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagem não encontrada.")
  return image

def get_recent_rasp_samples(db: Session) -> list:
  return repository.get_recent_rasp_samples(db)

def get_time_series(db: Session, days: int = 14, year: int | None = None, month: int | None = None) -> list:
  return repository.get_time_series(db, days, year, month)

def get_time_series_monthly(db: Session, year: int | None = None) -> list:
  return repository.get_time_series_monthly(db, year)

def get_time_series_hourly(db: Session, target_date: str) -> list:
  return repository.get_time_series_hourly(db, target_date)

def get_rasp_log(db: Session, limit: int = 20) -> list:
  return repository.get_rasp_log(db, limit)

def update_sample_tier(db: Session, code: str, tier: int):
  result = repository.update_tier(db, code, tier)
  if result is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Amostra '{code}' não encontrada.")
  return result

def delete_sample_by_code(db: Session, code: str) -> bool:
  return repository.delete_by_code(db, code)

def get_doctor_stats(db: Session) -> list:
  return repository.get_doctor_stats(db)

