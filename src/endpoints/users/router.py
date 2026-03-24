from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.dependencies import get_db
from src.endpoints.users.schema import UserCreate, UserCreatedResponse, LoginRequest, LoginResponse
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