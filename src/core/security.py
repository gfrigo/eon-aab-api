from datetime import datetime, timedelta, timezone

import jwt
from cryptography.fernet import Fernet, InvalidToken

from src.core.config import settings

ALGORITHM = "HS256"

def create_access_token(user_id: int, email: str) -> str:
  expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
  payload = {"sub": str(user_id), "email": email, "exp": expire}
  return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
  return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

# ── Criptografia reversível do PIN de dispositivo ──
# Não é um hash (irreversível) de propósito: o admin precisa poder consultar o
# PIN de novo pela plataforma. Isso evita guardar o PIN em texto puro no banco.
_fernet = Fernet(settings.TOKEN_ENCRYPTION_KEY.encode("utf-8"))

def encrypt_token(raw: str) -> str:
  return _fernet.encrypt(raw.encode("utf-8")).decode("utf-8")

def decrypt_token(encrypted: str) -> str | None:
  try:
    return _fernet.decrypt(encrypted.encode("utf-8")).decode("utf-8")
  except (InvalidToken, ValueError):
    return None
