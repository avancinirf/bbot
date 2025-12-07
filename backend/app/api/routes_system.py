from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.state import (
    get_system_running,
    toggle_system_running,
    set_system_running,
)

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
def health() -> dict:
    """Endpoint simples para checar se a API está de pé."""
    settings = get_settings()
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "app_mode": settings.app_mode,
    }


@router.get("/state")
def get_state() -> dict:
    """Retorna se o sistema está ligado ou desligado (em memória)."""
    return {"system_running": get_system_running()}


@router.post("/state/toggle")
def toggle_state() -> dict:
    """Liga/desliga o sistema (afeta a execução dos bots pelo engine)."""
    system_running = toggle_system_running()
    return {"system_running": system_running}


@router.post("/state/set")
def set_state(system_running: bool) -> dict:
    """
    Endpoint opcional para forçar um estado específico (true/false).
    Útil para depurar ou, no futuro, se quisermos um botão direto.
    """
    value = set_system_running(system_running)
    return {"system_running": value}
