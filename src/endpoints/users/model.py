from datetime import datetime
from sqlalchemy import Integer, String, Enum, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

class ProfileSettings(Base):
  __tablename__ = "ProfileSettings"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.id", ondelete="CASCADE", onupdate="CASCADE"), unique=True)
  language: Mapped[str] = mapped_column(String(10), nullable=False, default="pt-BR")
  timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="America/Sao_Paulo")
  notification_pref: Mapped[str] = mapped_column(String(20), nullable=False, default="email")
  ui_preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

  user = relationship("User", back_populates="profile_settings")

class User(Base):
  __tablename__ = "Users"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
  password: Mapped[str] = mapped_column(String(255), nullable=False)
  full_name: Mapped[str] = mapped_column(String(100), nullable=False)
  profile: Mapped[str] = mapped_column(
      Enum("admin", "analista", "visualizador"), nullable=False
  )
  is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

  profile_settings = relationship("ProfileSettings", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="joined")

  @property
  def avatar_url(self) -> str | None:
    if self.profile_settings and self.profile_settings.ui_preferences:
      return self.profile_settings.ui_preferences.get("avatar_url")
    return None