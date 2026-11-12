import secrets
import bcrypt
from sqlalchemy.orm import Session

from src.core.security import encrypt_token, decrypt_token
from src.endpoints.users.model import User
from src.endpoints.users.schema import UserCreate, LoginRequest
from src.endpoints.users import repository

def _hash(raw: str) -> str:
  return bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _generate_device_token(db: Session) -> str:
  """Gera um PIN de 4 dígitos que ainda não está em uso por nenhum usuário ativo
  (dispositivo genérico ou analista com PIN próprio)."""
  existing = {
    decrypt_token(u.api_token)
    for u in repository.get_all_users(db, skip=0, limit=1000)
    if u.api_token
  }
  for _ in range(50):
    candidate = f"{secrets.randbelow(10000):04d}"
    if candidate not in existing:
      return candidate
  raise ValueError("Não foi possível gerar um token único. Tente novamente.")

def generate_token_for_user(db: Session, user_id: int) -> str:
  """Gera (ou substitui) o PIN de acesso ao Rasp de um usuário já existente —
  usado pra dar um token próprio a um analista, sem criar um perfil novo."""
  user = repository.get_user_by_id(db, user_id)
  if not user:
    raise ValueError("Usuário não encontrado.")
  token = _generate_device_token(db)
  repository.set_api_token(db, user_id, encrypt_token(token))
  return token

def revoke_token_for_user(db: Session, user_id: int):
  user = repository.get_user_by_id(db, user_id)
  if not user:
    raise ValueError("Usuário não encontrado.")
  repository.set_api_token(db, user_id, None)

def create_user(db:Session, data:UserCreate) -> tuple[User, str | None]:
  """Cria um usuário. Para profile='dispositivo', gera um PIN de 4 dígitos — guardado
  criptografado no banco (não em texto puro, e não com hash irreversível: o admin precisa
  poder consultá-lo de novo na plataforma) em vez de email/senha — esse dispositivo nunca
  faz login na plataforma, só autentica o envio de amostras."""
  if data.profile == "dispositivo":
    slug = "".join(c for c in data.full_name.lower().replace(" ", "-") if c.isalnum() or c == "-") or "dispositivo"
    email = f"{slug}-{secrets.token_hex(3)}@device.eon.local"
    password_hash = _hash(secrets.token_urlsafe(24))
    device_token = _generate_device_token(db)
    user = repository.create_user(db, email, data.full_name, "dispositivo", password_hash, encrypt_token(device_token))
    return user, device_token

  if not data.email or not data.password:
    raise ValueError("Email e senha são obrigatórios para este perfil.")

  existing_user = repository.get_user_by_email(db, data.email)
  if existing_user:
    raise ValueError("Email já cadastrado.")

  user = repository.create_user(db, data.email, data.full_name, data.profile, _hash(data.password), None)
  return user, None

def login_user(db:Session, data:LoginRequest) -> User:
  user = repository.get_user_by_email(db, data.email)

  if not user or user.profile == "dispositivo":
    raise ValueError("Email ou senha inválidos.")

  password_match = bcrypt.checkpw(
    data.password.encode("utf-8"),
    user.password.encode("utf-8")
  )

  if not password_match:
    raise ValueError("Email ou senha inválidos.")

  if not user.is_active:
    raise ValueError("Usuário inativo.")

  return user

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
  return repository.get_all_users(db, skip, limit)

def update_avatar(db: Session, user_id: int, avatar_url: str):
  return repository.update_avatar(db, user_id, avatar_url)

def update_user(db: Session, user_id: int, data) -> User:
  user = repository.update_user(db, user_id, data.model_dump(exclude_unset=True))
  if not user: raise ValueError("Usuário não encontrado.")
  return user

def delete_user(db: Session, user_id: int):
  success = repository.delete_user(db, user_id)
  if not success: raise ValueError("Usuário não encontrado.")
