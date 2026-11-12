from fastapi import APIRouter, Depends, HTTPException, Request, status, File, UploadFile
from sqlalchemy.orm import Session
import os
import shutil
import uuid

from src.core.dependencies import get_db, get_current_user
from src.core.security import create_access_token, decrypt_token
from src.endpoints.users.schema import UserCreate, UserCreatedResponse, LoginRequest, LoginResponse, UserUpdate
from src.endpoints.users import service, repository

router = APIRouter(prefix="/users", tags=["Users"])

def _to_response(user, viewer) -> UserCreatedResponse:
  """Só expõe o PIN de acesso ao Rasp (descriptografado na hora) pra quem
  estiver logado como admin — de qualquer perfil que tenha um PIN configurado."""
  response = UserCreatedResponse.model_validate(user)
  if user.api_token and getattr(viewer, "profile", None) == "admin":
    response.device_token = decrypt_token(user.api_token)
  return response

@router.post("/signup", response_model=UserCreatedResponse, status_code=status.HTTP_201_CREATED)
def create_user(data:UserCreate, db:Session=Depends(get_db), _current_user=Depends(get_current_user)):
  try:
    user, _ = service.create_user(db, data)
    return _to_response(user, _current_user)
  except ValueError as e:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail=str(e),
    )

@router.post("/login", response_model=LoginResponse)
def login(data:LoginRequest, db:Session=Depends(get_db)):
  try:
    user = service.login_user(db, data)
    token = create_access_token(user.id, user.email)
    return LoginResponse(message="Login realizado com sucesso.", user=user, access_token=token)
  except ValueError as e:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail=str(e),
    )

@router.get("", response_model=list[UserCreatedResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  users = service.get_all_users(db, skip=skip, limit=limit)
  return [_to_response(u, _current_user) for u in users]

@router.put("/{user_id}", response_model=UserCreatedResponse)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  try:
    user = service.update_user(db, user_id, data)
    return _to_response(user, _current_user)
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  try:
    service.delete_user(db, user_id)
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{user_id}/token", response_model=UserCreatedResponse)
def generate_token(user_id: int, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  """Gera (ou substitui) o PIN de acesso ao Rasp de um usuário já existente —
  não cria um perfil novo, só adiciona/troca essa credencial na conta dele."""
  try:
    service.generate_token_for_user(db, user_id)
    user = repository.get_user_by_id(db, user_id)
    return _to_response(user, _current_user)
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{user_id}/token", response_model=UserCreatedResponse)
def revoke_token(user_id: int, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  try:
    service.revoke_token_for_user(db, user_id)
    user = repository.get_user_by_id(db, user_id)
    return _to_response(user, _current_user)
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{user_id}/avatar")
async def upload_avatar(user_id: int, request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
  ext = file.filename.split('.')[-1]
  filename = f"{uuid.uuid4()}.{ext}"
  filepath = os.path.join("uploads", filename)
  with open(filepath, "wb") as buffer:
      shutil.copyfileobj(file.file, buffer)

  avatar_url = f"{str(request.base_url).rstrip('/')}/uploads/{filename}"
  service.update_avatar(db, user_id, avatar_url)
  return {"avatar_url": avatar_url}