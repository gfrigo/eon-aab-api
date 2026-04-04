from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
import os
import shutil
import uuid

from src.core.dependencies import get_db
from src.endpoints.users.schema import UserCreate, UserCreatedResponse, LoginRequest, LoginResponse, UserUpdate
from src.endpoints.users import service

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/signup", response_model=UserCreatedResponse, status_code=status.HTTP_201_CREATED)
def create_user(data:UserCreate, db:Session=Depends(get_db)):
  try:
    return service.create_user(db, data)
  except ValueError as e:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail=str(e),
    )
  
@router.post("/login", response_model=LoginResponse)
def login(data:LoginRequest, db:Session=Depends(get_db)):
  try:
    user = service.login_user(db, data)
    return LoginResponse(message="Login realizado com sucesso.", user=user)
  except ValueError as e:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail=str(e),
    )

@router.get("", response_model=list[UserCreatedResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
  return service.get_all_users(db, skip=skip, limit=limit)

@router.put("/{user_id}", response_model=UserCreatedResponse)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
  try:
    return service.update_user(db, user_id, data)
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
  try:
    service.delete_user(db, user_id)
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{user_id}/avatar")
async def upload_avatar(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
  ext = file.filename.split('.')[-1]
  filename = f"{uuid.uuid4()}.{ext}"
  filepath = os.path.join("uploads", filename)
  with open(filepath, "wb") as buffer:
      shutil.copyfileobj(file.file, buffer)
  
  avatar_url = f"http://localhost:8000/uploads/{filename}"
  service.update_avatar(db, user_id, avatar_url)
  return {"avatar_url": avatar_url}