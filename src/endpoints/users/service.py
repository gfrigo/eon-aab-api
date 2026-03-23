from sqlalchemy.orm import Session
from passlib.context import CryptContext

from src.endpoints.users.model import User
from src.endpoints.users.schema import UserCreate
from src.endpoints.users import repository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db:Session, data:UserCreate) -> User:
  existing_user = repository.get_user_by_email(db, data.email)

  if existing_user:
    raise ValueError("Email já cadastrado.")

  hashed_password = pwd_context.hash(data.password)
  
  user = repository.create_user(db, data, hashed_password)
  return user