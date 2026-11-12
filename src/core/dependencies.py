import time
from collections import defaultdict
from collections.abc import Generator

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.core.database import SessionLocal
from src.core.security import decode_access_token, decrypt_token

def get_db() -> Generator[Session, None, None]:
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
  credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
  db: Session = Depends(get_db),
):
  """Valida o token JWT do header Authorization e retorna o usuário logado."""
  unauthorized = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Não autenticado.",
    headers={"WWW-Authenticate": "Bearer"},
  )
  if credentials is None:
    raise unauthorized

  try:
    payload = decode_access_token(credentials.credentials)
    user_id = int(payload["sub"])
  except (jwt.PyJWTError, KeyError, ValueError):
    raise unauthorized

  from src.endpoints.users.model import User
  user = db.query(User).filter(User.id == user_id).first()
  if not user or not user.is_active:
    raise unauthorized

  return user

# ── Autenticação de dispositivo (PIN de 4 dígitos da Raspberry Pi) ──
# Limite simples de tentativas por IP para dificultar força bruta sobre o PIN curto.
_device_auth_failures: dict[str, list[float]] = defaultdict(list)
_DEVICE_MAX_FAILURES = 8
_DEVICE_WINDOW_SECONDS = 300

def get_current_device(
  request: Request,
  credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
  db: Session = Depends(get_db),
):
  """Valida o PIN do header Authorization e retorna o usuário correspondente
  (dispositivo genérico ou analista com PIN próprio). Usado só pela rota de
  ingestão da Raspberry Pi."""
  unauthorized = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token de dispositivo inválido.",
    headers={"WWW-Authenticate": "Bearer"},
  )

  client_ip = request.client.host if request.client else "unknown"
  now = time.time()
  attempts = [t for t in _device_auth_failures[client_ip] if now - t < _DEVICE_WINDOW_SECONDS]
  _device_auth_failures[client_ip] = attempts
  if len(attempts) >= _DEVICE_MAX_FAILURES:
    raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Muitas tentativas. Tente novamente em alguns minutos.")

  if credentials is None:
    _device_auth_failures[client_ip].append(now)
    raise unauthorized

  from src.endpoints.users.model import User
  token = credentials.credentials.strip()
  candidates = (
    db.query(User)
    .filter(User.is_active == 1, User.api_token.isnot(None))
    .all()
  )
  for candidate in candidates:
    if decrypt_token(candidate.api_token) == token:
      return candidate

  _device_auth_failures[client_ip].append(now)
  raise unauthorized