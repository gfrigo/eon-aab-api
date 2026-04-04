from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.dependencies import get_db
from src.endpoints.samples.schema import SampleCreate, SampleResponse
from src.endpoints.samples import service

router = APIRouter(prefix="/samples", tags=["Samples"])

@router.get("", response_model=list[SampleResponse])
def get_samples(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
  return service.get_samples(db, skip=skip, limit=limit)

@router.post("", response_model=SampleResponse, status_code=status.HTTP_201_CREATED)
def create_sample(data: SampleCreate, db: Session = Depends(get_db)):
  return service.create_sample(db, data)
