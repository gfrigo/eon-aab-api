from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

class Batch(Base):
  __tablename__ = "Batches"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.id"), nullable=False)
  code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

class Sample(Base):
  __tablename__ = "Samples"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  batch_id: Mapped[int] = mapped_column(Integer, ForeignKey("Batches.id"), nullable=False)
  code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
  created_by: Mapped[int] = mapped_column(Integer, ForeignKey("Users.id"), nullable=False)
  tier: Mapped[int | None] = mapped_column(Integer, nullable=True)
  tier_label: Mapped[str | None] = mapped_column(String(20), nullable=True)
  status: Mapped[str] = mapped_column(
      Enum("pendente", "processando", "concluido", "rejeitado"), nullable=False, default="pendente"
  )
  collected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
  analyzed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

class SampleResult(Base):
  __tablename__ = "SampleResults"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  sample_id: Mapped[int] = mapped_column(Integer, ForeignKey("Samples.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, unique=True)
  image_path: Mapped[str] = mapped_column(String(500), nullable=False)
  confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
  ml_raw_output: Mapped[dict | None] = mapped_column(JSON, nullable=True)
  model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
  processed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
