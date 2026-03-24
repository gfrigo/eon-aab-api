from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Literal

class UserCreate(BaseModel):
  email: EmailStr
  password: str
  full_name: str
  profile: Literal["admin", "analista", "visualizador"]
 
class UserCreatedResponse(BaseModel):
  id: int
  email: str
  full_name: str
  profile: str
  is_active: int
  created_at: datetime
  updated_at: datetime

  model_config = {"from_attributes": True}

class LoginRequest(BaseModel):
  email: EmailStr
  password: str

class LoginResponse(BaseModel):
  message: str
  user: UserCreatedResponse

  model_config = {"from_attributes": True}