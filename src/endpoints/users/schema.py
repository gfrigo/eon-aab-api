from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

PROFILES = Literal["admin", "analista", "visualizador", "dispositivo"]

class UserCreate(BaseModel):
  email: Optional[EmailStr] = None
  password: Optional[str] = None
  full_name: str
  profile: PROFILES

class UserUpdate(BaseModel):
  full_name: Optional[str] = None
  profile: Optional[PROFILES] = None
  is_active: Optional[int] = None

class UserCreatedResponse(BaseModel):
  id: int
  email: str
  full_name: str
  profile: str
  is_active: int
  created_at: datetime
  updated_at: datetime
  avatar_url: Optional[str] = None
  device_token: Optional[str] = None  # só preenchido na criação de um usuário "dispositivo"

  model_config = {"from_attributes": True}

class LoginRequest(BaseModel):
  email: EmailStr
  password: str

class LoginResponse(BaseModel):
  message: str
  user: UserCreatedResponse
  access_token: str
  token_type: str = "bearer"

  model_config = {"from_attributes": True}