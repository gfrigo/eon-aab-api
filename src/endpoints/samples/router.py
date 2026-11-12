import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from src.core.dependencies import get_db, get_current_user, get_current_device
from src.endpoints.samples.schema import (
  SampleCreate, SampleResponse, DashboardResponse, SampleWithImageResponse,
  GalleryItemResponse, RaspStatusResponse, PendingCountResponse, RaspSampleCreate,
  RecentSampleResponse, TimeSeriesItem, RaspLogItem, DoctorStatItem, SampleTierUpdate,
)
from src.endpoints.samples import service

router = APIRouter(prefix="/samples", tags=["Samples"])

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  return service.get_dashboard(db)

@router.get("/by-code/{code}", response_model=SampleWithImageResponse)
def get_sample_by_code(code: str, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  return service.get_sample_by_code(db, code)

@router.get("/by-code/{code}/image")
def get_sample_image(code: str, db: Session = Depends(get_db)):
  """Serve a foto guardada no banco. Sem auth, igual ao /uploads estático
  que ela substitui — é assim que as tags <img> do painel conseguem carregá-la."""
  image = service.get_sample_image(db, code)
  return Response(content=image, media_type="image/jpeg")

@router.patch("/by-code/{code}", response_model=SampleResponse)
def update_sample_tier(code: str, data: SampleTierUpdate, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  return service.update_sample_tier(db, code, data.tier)

@router.delete("/by-code/{code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sample_by_code(code: str, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  deleted = service.delete_sample_by_code(db, code)
  if not deleted:
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=f"Amostra '{code}' não encontrada.")

@router.get("", response_model=list[SampleResponse])
def get_samples(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  return service.get_samples(db, skip=skip, limit=limit)

@router.post("", response_model=SampleResponse, status_code=status.HTTP_201_CREATED)
def create_sample(data: SampleCreate, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  return service.create_sample(db, data)

@router.get("/gallery", response_model=list[GalleryItemResponse])
def get_gallery(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  return service.get_gallery(db)

@router.get("/rasp-status", response_model=RaspStatusResponse)
def get_rasp_status(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  return service.get_rasp_status(db)

@router.get("/pending-count", response_model=PendingCountResponse)
def get_pending_count(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  return service.get_pending_count(db)

# Rota usada pela própria Raspberry Pi para enviar leituras — autenticada com o
# PIN de 4 dígitos do usuário "dispositivo" (gerado em Usuários), não com o
# login normal.
@router.post("/rasp", response_model=SampleResponse, status_code=status.HTTP_201_CREATED)
def create_rasp_sample(data: RaspSampleCreate, db: Session = Depends(get_db), device=Depends(get_current_device)):
  return service.create_rasp_sample(db, data, device)

@router.post("/rasp/verify")
def verify_rasp_token(device=Depends(get_current_device)):
  """Usado pelo kiosk do Rasp para validar o PIN de acesso digitado na tela de
  login contra a plataforma, em vez de comparar com um valor fixo local."""
  return {"valid": True, "name": device.full_name}

@router.post("/rasp/capture", response_model=SampleResponse, status_code=status.HTTP_201_CREATED)
def capture_rasp_sample(
  photo_id: str = Form(...),
  collected_at: datetime = Form(...),
  tier: int | None = Form(None),
  image: UploadFile = File(...),
  db: Session = Depends(get_db),
  device=Depends(get_current_device),
):
  """Recebe a foto capturada pelo Rasp. Se o operador já selecionou o grau na
  tela do kiosk, a amostra é registrada direto com esse grau (rótulo manual).
  Sem grau, fica 'pendente' aguardando avaliação manual no painel."""
  if tier is not None and tier not in (1, 2, 3, 4):
    raise HTTPException(status_code=400, detail="Grau inválido — use 1 a 4.")
  ext = (image.filename or "").rsplit(".", 1)[-1].lower() if "." in (image.filename or "") else "jpg"
  if ext not in ("jpg", "jpeg", "png"):
    raise HTTPException(status_code=400, detail="Formato de imagem não suportado.")
  filename = f"{uuid.uuid4()}.{ext}"
  image_bytes = image.file.read()

  return service.create_pending_rasp_sample(db, photo_id, filename, image_bytes, collected_at, device, tier)

@router.get("/recent", response_model=list[RecentSampleResponse])
def get_recent(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  return service.get_recent_rasp_samples(db)

@router.get("/time-series", response_model=list[TimeSeriesItem])
def get_time_series(days: int = 14, year: int | None = None, month: int | None = None, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  return service.get_time_series(db, days, year, month)

@router.get("/time-series-monthly", response_model=list[TimeSeriesItem])
def get_time_series_monthly(year: int | None = None, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  return service.get_time_series_monthly(db, year)

@router.get("/time-series-hourly", response_model=list[TimeSeriesItem])
def get_time_series_hourly(date: str, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  return service.get_time_series_hourly(db, date)

@router.get("/rasp-log", response_model=list[RaspLogItem])
def get_rasp_log(limit: int = 20, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  return service.get_rasp_log(db, limit)

@router.get("/doctor-stats", response_model=list[DoctorStatItem])
def get_doctor_stats(db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  return service.get_doctor_stats(db)

