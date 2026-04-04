from sqlalchemy.orm import Session
from src.endpoints.samples.model import Sample
from src.endpoints.samples.schema import SampleCreate
from src.endpoints.samples import repository

def get_samples(db: Session, skip: int = 0, limit: int = 100) -> list[Sample]:
  return repository.get_all(db, skip, limit)

def create_sample(db: Session, data: SampleCreate) -> Sample:
  return repository.create(db, data)
