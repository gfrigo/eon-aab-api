from datetime import datetime
from sqlalchemy import Integer, String, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

class User(Base):
  __tablename__ = "ABS_Users"

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