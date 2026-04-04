from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

class UserCreate(BaseModel):
  email: EmailStr
  password: str
  full_name: str
  profile: Literal["admin", "analista", "visualizador"]
 
class UserUpdate(BaseModel):
  full_name: Optional[str] = None
  profile: Optional[Literal["admin", "analista", "visualizador"]] = None
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

  model_config = {"from_attributes": True}

class LoginRequest(BaseModel):
  email: EmailStr
  password: str

class LoginResponse(BaseModel):
  message: str
  user: UserCreatedResponse

  model_config = {"from_attributes": True}