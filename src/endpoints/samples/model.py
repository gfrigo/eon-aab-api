from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

class Sample(Base):
  __tablename__ = "Samples"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
  created_by: Mapped[int] = mapped_column(Integer, ForeignKey("Users.id"), nullable=False)
  analyzed_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("Users.id"), nullable=True)
  tier: Mapped[int | None] = mapped_column(Integer, nullable=True)
  tier_label: Mapped[str | None] = mapped_column(String(20), nullable=True)
  status: Mapped[str] = mapped_column(
      Enum("pendente", "processando", "concluido", "rejeitado"), nullable=False, default="pendente"
  )
  collected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
  analyzed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
