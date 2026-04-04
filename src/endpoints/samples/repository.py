from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.endpoints.samples.model import Sample
from src.endpoints.samples.schema import SampleCreate

def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Sample]:
  return db.query(Sample).offset(skip).limit(limit).all()

def create(db: Session, data: SampleCreate) -> Sample:
  now = datetime.now(timezone.utc)
  new_sample = Sample(
    code=data.code,
    created_by=data.created_by,
    collected_at=data.collected_at,
    created_at=now,
    status="pendente"
  )
  db.add(new_sample)
  db.commit()
  db.refresh(new_sample)
  return new_sample
