from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.dependencies import get_db
from src.endpoints.samples.schema import (
  SampleCreate, SampleResponse, DashboardResponse, SampleWithImageResponse,
  GalleryItemResponse, RaspStatusResponse, PendingCountResponse, RaspSampleCreate,
  RecentSampleResponse,
)
from src.endpoints.samples import service

router = APIRouter(prefix="/samples", tags=["Samples"])

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
  return service.get_dashboard(db)

@router.get("/by-code/{code}", response_model=SampleWithImageResponse)
def get_sample_by_code(code: str, db: Session = Depends(get_db)):
  return service.get_sample_by_code(db, code)

@router.get("", response_model=list[SampleResponse])
def get_samples(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
  return service.get_samples(db, skip=skip, limit=limit)

@router.post("", response_model=SampleResponse, status_code=status.HTTP_201_CREATED)
def create_sample(data: SampleCreate, db: Session = Depends(get_db)):
  return service.create_sample(db, data)

@router.get("/gallery", response_model=list[GalleryItemResponse])
def get_gallery(db: Session = Depends(get_db)):
  return service.get_gallery(db)

@router.get("/rasp-status", response_model=RaspStatusResponse)
def get_rasp_status(db: Session = Depends(get_db)):
  return service.get_rasp_status(db)

@router.get("/pending-count", response_model=PendingCountResponse)
def get_pending_count(db: Session = Depends(get_db)):
  return service.get_pending_count(db)

@router.post("/rasp", response_model=SampleResponse, status_code=status.HTTP_201_CREATED)
def create_rasp_sample(data: RaspSampleCreate, db: Session = Depends(get_db)):
  return service.create_rasp_sample(db, data)

@router.get("/recent", response_model=list[RecentSampleResponse])
def get_recent(db: Session = Depends(get_db)):
  return service.get_recent_rasp_samples(db)

