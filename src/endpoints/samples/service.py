from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.endpoints.samples.model import Sample
from src.endpoints.samples.schema import SampleCreate
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

