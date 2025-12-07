from __future__ import annotations

from typing import Dict


# Estado global simples em memória.
# Por enquanto só temos system_running, mas se precisar
# podemos guardar mais coisas aqui depois.
_state: Dict[str, bool] = {
    "system_running": False,
}


def get_system_running() -> bool:
    return _state["system_running"]


def set_system_running(value: bool) -> bool:
    _state["system_running"] = bool(value)
    return _state["system_running"]


def toggle_system_running() -> bool:
    _state["system_running"] = not _state["system_running"]
    return _state["system_running"]
