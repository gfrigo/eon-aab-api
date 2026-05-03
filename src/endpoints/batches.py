from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.dependencies import get_db
from src.endpoints.samples.model import Batch, Sample

router = APIRouter(prefix="/batches", tags=["Batches"])

class BatchCreate(BaseModel):
    user_id: int
    code: str

class BatchResponse(BaseModel):
    id: int
    user_id: int
    code: str
    created_at: datetime
    total_samples: int
    completed: int
    rejected: int
    pending: int

@router.get("", response_model=list[BatchResponse])
def list_batches(db: Session = Depends(get_db)):
    batches = db.query(Batch).order_by(Batch.created_at.desc()).all()
    result = []
    for b in batches:
        samples = db.query(Sample).filter(Sample.batch_id == b.id).all()
        result.append({
            "id": b.id,
            "user_id": b.user_id,
            "code": b.code,
            "created_at": b.created_at,
            "total_samples": len(samples),
            "completed": sum(1 for s in samples if s.status == "concluido"),
            "rejected": sum(1 for s in samples if s.status == "rejeitado"),
            "pending": sum(1 for s in samples if s.status in ("pendente", "processando")),
        })
    return result

@router.post("", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(data: BatchCreate, db: Session = Depends(get_db)):
    existing = db.query(Batch).filter(Batch.code == data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Código de lote já existe.")
    batch = Batch(
        user_id=data.user_id,
        code=data.code.upper(),
        created_at=datetime.now(timezone.utc)
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return {
        "id": batch.id,
        "user_id": batch.user_id,
        "code": batch.code,
        "created_at": batch.created_at,
        "total_samples": 0,
        "completed": 0,
        "rejected": 0,
        "pending": 0,
    }
