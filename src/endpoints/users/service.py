import bcrypt
from sqlalchemy.orm import Session

from src.endpoints.users.model import User
from src.endpoints.users.schema import UserCreate, LoginRequest
from src.endpoints.users import repository

def create_user(db:Session, data:UserCreate) -> User:
  existing_user = repository.get_user_by_email(db, data.email)

  if existing_user:
    raise ValueError("Email já cadastrado.")

  hashed_password = bcrypt.hashpw(
    data.password.encode("utf-8"),
    bcrypt.gensalt()
  ).decode("utf-8")
  
  user = repository.create_user(db, data, hashed_password)
  return user

def login_user(db:Session, data:LoginRequest) -> User:
  user = repository.get_user_by_email(db, data.email)

  if not user:
    raise ValueError("Email ou senha inválidos.")

  password_match = bcrypt.checkpw(
    data.password.encode("utf-8"),
    user.password.encode("utf-8")
  )

  if not password_match:
    raise ValueError("Email ou senha inválidos.")

  if not user.is_active:
    raise ValueError("Usuário inativo.")

  return user