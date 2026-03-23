import logging
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("uvicorn")

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
  DB_HOST: str | None = None
  DB_USER: str | None = None
  DB_PASSWORD: str | None = None
  DB_SCHEMA: str | None = None
  DB_PORT: int | None = 3306

  @property
  def database_url(self) -> str:
    return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_SCHEMA}"

  model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")

settings = Settings()