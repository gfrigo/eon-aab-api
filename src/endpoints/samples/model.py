from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, Float, JSON, BigInteger
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

class SampleFile(Base):
  __tablename__ = "SampleFiles"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  sample_id: Mapped[int] = mapped_column(Integer, ForeignKey("Samples.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
  file_name: Mapped[str] = mapped_column(String(255), nullable=False)
  file_type: Mapped[str] = mapped_column(String(50), nullable=False)
  storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
  file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
  checksum: Mapped[str] = mapped_column(String(64), nullable=False)
  uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

class SampleResult(Base):
  __tablename__ = "SampleResults"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  sample_id: Mapped[int] = mapped_column(Integer, ForeignKey("Samples.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, unique=True)
  confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
  ml_raw_output: Mapped[dict] = mapped_column(JSON, nullable=False)
  model_version: Mapped[str] = mapped_column(String(50), nullable=False)
  processed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
