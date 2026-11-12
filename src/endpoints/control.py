"""Controle físico do Raspberry Pi: reiniciar, Wi-Fi, reiniciar captura, etc.,
e um terminal remoto (shell persistente via PTY) para o painel 'Raspberry' da
plataforma. Só faz sentido quando este backend roda NO PRÓPRIO dispositivo —
por isso cada ação confirma que está em Linux antes de executar qualquer
comando de sistema."""

import asyncio
import os
import platform
import struct
import subprocess
import threading

# fcntl/pty/termios só existem em Linux/Unix — importados sob demanda no
# terminal_ws (que já recusa conexão se platform.system() != "Linux"), pra
# não quebrar o import deste módulo quando o backend roda no Windows (dev).

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from src.core.dependencies import get_db, get_current_user
from src.core.security import decode_access_token
from src.endpoints.users.repository import get_user_by_id

router = APIRouter(prefix="/raspberry", tags=["Raspberry Control"])

EON_UI_DATA_DIR = os.path.expanduser("~/eon-ui/dados")


def _require_admin(user):
  if getattr(user, "profile", None) != "admin":
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas administradores podem controlar o dispositivo.")


def _require_linux():
  if platform.system() != "Linux":
    raise HTTPException(
      status_code=status.HTTP_501_NOT_IMPLEMENTED,
      detail="Este backend não está rodando no Raspberry Pi — ação de controle indisponível aqui.",
    )


def _run(cmd: list[str], timeout: int = 15) -> dict:
  try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
      raise HTTPException(status_code=500, detail=(result.stderr or result.stdout or "Comando falhou.").strip()[:400])
    return {"ok": True, "output": (result.stdout or "").strip()[:2000]}
  except subprocess.TimeoutExpired:
    raise HTTPException(status_code=504, detail="Comando demorou demais e foi cancelado.")
  except FileNotFoundError:
    raise HTTPException(status_code=501, detail=f"Comando não encontrado: {cmd[0]}")


def _run_delayed(cmd: list[str], delay: float = 1.5):
  """Agenda o comando pra rodar um pouco depois, pra dar tempo da resposta HTTP
  chegar ao cliente antes do processo (ou a máquina) cair."""
  def _target():
    import time
    time.sleep(delay)
    subprocess.run(cmd)
  threading.Thread(target=_target, daemon=True).start()


@router.post("/control/reboot")
def reboot(db: Session = Depends(get_db), user=Depends(get_current_user)):
  _require_admin(user)
  _require_linux()
  _run_delayed(["sudo", "/usr/bin/systemctl", "reboot"])
  return {"ok": True, "message": "Reiniciando em instantes."}


@router.post("/control/shutdown")
def shutdown(db: Session = Depends(get_db), user=Depends(get_current_user)):
  _require_admin(user)
  _require_linux()
  _run_delayed(["sudo", "/usr/bin/systemctl", "poweroff"])
  return {"ok": True, "message": "Desligando em instantes."}


@router.post("/control/wifi-cycle")
def wifi_cycle(db: Session = Depends(get_db), user=Depends(get_current_user)):
  _require_admin(user)
  _require_linux()
  _run(["sudo", "/usr/bin/nmcli", "radio", "wifi", "off"], timeout=10)
  import time
  time.sleep(2)
  return _run(["sudo", "/usr/bin/nmcli", "radio", "wifi", "on"], timeout=10)


@router.post("/control/restart-capture")
def restart_capture(db: Session = Depends(get_db), user=Depends(get_current_user)):
  _require_admin(user)
  _require_linux()
  return _run(["sudo", "/usr/bin/systemctl", "restart", "eon-ui.service"])


@router.post("/control/sync-clock")
def sync_clock(db: Session = Depends(get_db), user=Depends(get_current_user)):
  _require_admin(user)
  _require_linux()
  return _run(["sudo", "/usr/bin/systemctl", "restart", "systemd-timesyncd.service"])


@router.post("/control/clear-cache")
def clear_cache(db: Session = Depends(get_db), user=Depends(get_current_user)):
  _require_admin(user)
  _require_linux()
  if not os.path.isdir(EON_UI_DATA_DIR):
    return {"ok": True, "output": "Nada para limpar."}
  removed = 0
  for name in os.listdir(EON_UI_DATA_DIR):
    path = os.path.join(EON_UI_DATA_DIR, name)
    if os.path.isdir(path) and name.startswith("lote_"):
      subprocess.run(["rm", "-rf", path])
      removed += 1
  return {"ok": True, "output": f"{removed} lote(s) local(is) removido(s)."}


@router.post("/control/check-update")
def check_update(db: Session = Depends(get_db), user=Depends(get_current_user)):
  _require_admin(user)
  _require_linux()
  # Deploy atual não usa git — não há canal de atualização automática ainda.
  return {"ok": True, "output": "Sem mecanismo de atualização automática configurado neste deploy."}


# ───────────────────────────── Terminal remoto (PTY real) ─────────────────────

def _authenticate_ws(db: Session, token: str):
  try:
    payload = decode_access_token(token)
    user = get_user_by_id(db, int(payload["sub"]))
  except Exception:
    return None
  if not user or getattr(user, "profile", None) != "admin":
    return None
  return user


@router.websocket("/control/terminal")
async def terminal_ws(websocket: WebSocket, token: str = "", db: Session = Depends(get_db)):
  await websocket.accept()

  if platform.system() != "Linux":
    await websocket.send_json({"type": "error", "data": "Backend não está rodando no Raspberry Pi."})
    await websocket.close()
    return

  user = _authenticate_ws(db, token)
  if not user:
    await websocket.send_json({"type": "error", "data": "Não autorizado."})
    await websocket.close(code=4401)
    return

  import fcntl
  import pty
  import termios

  pid, fd = pty.fork()
  if pid == 0:
    env = {**os.environ, "TERM": "dumb", "PS1": "$ "}
    os.execve("/bin/bash", ["/bin/bash", "--norc", "--noprofile"], env)
    return

  loop = asyncio.get_event_loop()
  os.set_blocking(fd, False)

  async def read_pty():
    while True:
      try:
        data = os.read(fd, 4096)
      except (OSError, BlockingIOError):
        await asyncio.sleep(0.05)
        continue
      if not data:
        break
      await websocket.send_json({"type": "output", "data": data.decode(errors="replace")})

  reader_task = loop.create_task(read_pty())
  try:
    while True:
      msg = await websocket.receive_json()
      if msg.get("type") == "input":
        os.write(fd, msg["data"].encode())
      elif msg.get("type") == "resize":
        rows, cols = int(msg.get("rows", 24)), int(msg.get("cols", 80))
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
  except WebSocketDisconnect:
    pass
  finally:
    reader_task.cancel()
    try:
      os.kill(pid, 9)
    except ProcessLookupError:
      pass
    os.close(fd)
