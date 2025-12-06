from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session, SQLModel

from app.db.models import SystemState
from app.db.session import get_session

router = APIRouter(prefix="/system", tags=["system"])


# ---------- Schemas Pydantic/SQLModel para API ----------

class SystemStateRead(SQLModel):
    id: int
    online: bool
    simulation_mode: bool
    created_at: datetime
    updated_at: datetime


class SystemStateUpdate(SQLModel):
    online: Optional[bool] = None
    simulation_mode: Optional[bool] = None


# ---------- Rotas ----------

@router.get("/state", response_model=SystemStateRead)
def get_system_state(session: Session = Depends(get_session)) -> SystemState:
    """
    Retorna o estado global do sistema.
    Se não existir, cria um padrão.
    """
    state = session.get(SystemState, 1)
    if not state:
        state = SystemState(id=1, online=False, simulation_mode=True)
        session.add(state)
        session.commit()
        session.refresh(state)
    return state


@router.put("/state", response_model=SystemStateRead)
def update_system_state(
    payload: SystemStateUpdate,
    session: Session = Depends(get_session),
) -> SystemState:
    """
    Atualiza flags de online/simulation_mode.
    Somente campos enviados no payload são alterados.
    """
    state = session.get(SystemState, 1)
    if not state:
        state = SystemState(id=1, online=False, simulation_mode=True)
        session.add(state)
        session.commit()
        session.refresh(state)

    # Atualiza apenas campos enviados
    if payload.online is not None:
        state.online = payload.online
    if payload.simulation_mode is not None:
        state.simulation_mode = payload.simulation_mode

    state.updated_at = datetime.utcnow()
    session.add(state)
    session.commit()
    session.refresh(state)
    return state
