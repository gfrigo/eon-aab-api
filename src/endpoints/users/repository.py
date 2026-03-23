from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.endpoints.users.model import User
from src.endpoints.users.schema import UserCreate

def get_user_by_email(db:Session, email:str) -> User | None:
  return db.query(User).filter(User.email == email).first()

def create_user(db:Session, data:UserCreate, hashed_password:str) -> User:
  now = datetime.now(timezone.utc)

  user = User(
    email=data.email,
    password=hashed_password,
    full_name=data.full_name,
    profile=data.profile,
    is_active=1,
    created_at=now,
    updated_at=now,
  )

  db.add(user)
  db.commit()
  db.refresh(user)

  return user