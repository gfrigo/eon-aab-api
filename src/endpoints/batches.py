from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.dependencies import get_db, get_current_user
from src.core.security import decrypt_token
from src.endpoints.samples.model import Batch, Sample, SampleResult
from src.endpoints.users.model import User

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

class BatchSampleItem(BaseModel):
    code: str
    tier: int | None
    tier_label: str | None
    status: str
    collected_at: datetime
    analyzed_at: datetime | None
    created_at: datetime
    created_by_name: str
    created_by_profile: str
    device_token: str | None = None
    confidence_score: float | None = None
    processed_at: datetime | None = None

@router.get("/{batch_id}/samples", response_model=list[BatchSampleItem])
def get_batch_samples(batch_id: int, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
    """Lista as amostras de um lote com quem coletou/analisou cada uma.
    O PIN do dispositivo/usuário só é decriptado e exposto para quem está logado como admin."""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Lote não encontrado.")

    is_admin = getattr(_current_user, "profile", None) == "admin"
    samples = db.query(Sample).filter(Sample.batch_id == batch_id).order_by(Sample.collected_at.desc()).all()

    result = []
    for s in samples:
        creator = db.query(User).filter(User.id == s.created_by).first()
        sr = db.query(SampleResult).filter(SampleResult.sample_id == s.id).first()
        token = None
        if is_admin and creator and creator.api_token:
            token = decrypt_token(creator.api_token)
        result.append({
            "code": s.code,
            "tier": s.tier,
            "tier_label": s.tier_label,
            "status": s.status,
            "collected_at": s.collected_at,
            "analyzed_at": s.analyzed_at,
            "created_at": s.created_at,
            "created_by_name": creator.full_name if creator else "—",
            "created_by_profile": creator.profile if creator else "—",
            "device_token": token,
            "confidence_score": sr.confidence_score if sr else None,
            "processed_at": sr.processed_at if sr else None,
        })
    return result

@router.get("", response_model=list[BatchResponse])
def list_batches(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
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

@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_batch(batch_id: int, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
    """Remove um lote e todas as amostras/resultados associados."""
    from src.endpoints.samples.model import SampleResult
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Lote não encontrado.")
    samples = db.query(Sample).filter(Sample.batch_id == batch_id).all()
    for sample in samples:
        db.query(SampleResult).filter(SampleResult.sample_id == sample.id).delete()
    db.query(Sample).filter(Sample.batch_id == batch_id).delete()
    db.delete(batch)
    db.commit()

@router.post("", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(data: BatchCreate, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
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
