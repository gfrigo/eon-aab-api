import logging
from typing import Dict
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

  @property
  def db_credentials(self) -> Dict[str, str]:
    return {
      "host": self.DB_HOST,
      "user": self.DB_USER,
      "password": self.DB_PASSWORD,
      "schema": self.DB_SCHEMA,
    }

  model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")

settings = Settings()