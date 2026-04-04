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

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
  return db.query(User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, data: dict) -> User | None:
  user = db.query(User).filter(User.id == user_id).first()
  if not user: return None
  
  if "full_name" in data and data["full_name"] is not None: user.full_name = data["full_name"]
  if "profile" in data and data["profile"] is not None: user.profile = data["profile"]
  if "is_active" in data and data["is_active"] is not None: user.is_active = data["is_active"]
  
  user.updated_at = datetime.now(timezone.utc)
  db.commit()
  db.refresh(user)
  return user

def delete_user(db: Session, user_id: int) -> bool:
  user = db.query(User).filter(User.id == user_id).first()
  if not user: return False
  db.delete(user)
  db.commit()
  return True

def update_avatar(db: Session, user_id: int, avatar_url: str):
  from src.endpoints.users.model import ProfileSettings
  profile = db.query(ProfileSettings).filter(ProfileSettings.user_id == user_id).first()
  if not profile:
    profile = ProfileSettings(user_id=user_id, ui_preferences={"avatar_url": avatar_url})
    db.add(profile)
  else:
    prefs = dict(profile.ui_preferences or {})
    prefs["avatar_url"] = avatar_url
    profile.ui_preferences = prefs
  db.commit()
  return profile