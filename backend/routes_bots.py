# ==== BLOCK: ROUTES_BOTS_IMPORTS - START ====
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from datetime import datetime
from pydantic import BaseModel

from .models import Bot, BotAsset
from .db import get_session
from .bot_init import initialize_bot_balances
# ==== BLOCK: ROUTES_BOTS_IMPORTS - END ====



# ==== BLOCK: ROUTES_BOTS_ROUTER - START ====
router = APIRouter(prefix="/api/bots", tags=["bots"])
# ==== BLOCK: ROUTES_BOTS_ROUTER - END ====


# ==== BLOCK: ROUTES_BOTS_SCHEMAS - START ====
class BotCreate(BaseModel):
    """
    Schema para criação de Bot.
    """
    name: str
    is_active: bool = False
    initial_balance_usdt: float = 0.0
    current_balance_usdt: float = 0.0
    stop_behavior: str = "STOP_ONLY"
    stop_loss_percent: float = 40.0
# ==== BLOCK: ROUTES_BOTS_SCHEMAS - END ====


# ==== BLOCK: ROUTES_BOTS_LIST - START ====
@router.get("/", response_model=List[Bot])
def list_bots(session: Session = Depends(get_session)):
    statement = select(Bot).order_by(Bot.id)
    bots = session.exec(statement).all()
    return bots
# ==== BLOCK: ROUTES_BOTS_LIST - END ====


# ==== BLOCK: ROUTES_BOTS_ACTIVE_GET - START ====
@router.get("/active", response_model=Optional[Bot])
def get_active_bot(session: Session = Depends(get_session)):
    """
    Retorna o bot ativo (se existir).
    """
    statement = select(Bot).where(Bot.is_active == True)  # noqa: E712
    bot = session.exec(statement).first()
    return bot
# ==== BLOCK: ROUTES_BOTS_ACTIVE_GET - END ====


# ==== BLOCK: ROUTES_BOTS_GET_ONE - START ====
@router.get("/{bot_id}", response_model=Bot)
def get_bot(bot_id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")
    return bot
# ==== BLOCK: ROUTES_BOTS_GET_ONE - END ====


# ==== BLOCK: ROUTES_BOTS_CREATE - START ====
@router.post("/", response_model=Bot)
def create_bot(bot_data: BotCreate, session: Session = Depends(get_session)):
    db_bot = Bot(
        name=bot_data.name,
        is_active=bot_data.is_active,
        initial_balance_usdt=bot_data.initial_balance_usdt,
        current_balance_usdt=bot_data.current_balance_usdt,
        stop_behavior=bot_data.stop_behavior,
        stop_loss_percent=bot_data.stop_loss_percent,
    )
    session.add(db_bot)
    session.commit()
    session.refresh(db_bot)
    return db_bot
# ==== BLOCK: ROUTES_BOTS_CREATE - END ====


# ==== BLOCK: ROUTES_BOTS_UPDATE_SCHEMA - START ====
class BotUpdate(BaseModel):
    name: Optional[str] = None
    initial_balance_usdt: Optional[float] = None
    stop_loss_percent: Optional[float] = None
    stop_behavior: Optional[str] = None
# ==== BLOCK: ROUTES_BOTS_UPDATE_SCHEMA - END ====


# ==== BLOCK: ROUTES_BOTS_ACTIVATE - START ====
@router.patch("/{bot_id}/activate", response_model=Bot)
def activate_bot(bot_id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")

    # Desativar todos os bots
    stmt_all = select(Bot)
    all_bots = session.exec(stmt_all).all()
    for b in all_bots:
        if b.is_active:
            b.is_active = False

    # Ativar o bot escolhido
    bot.is_active = True
    session.add(bot)
    session.commit()
    session.refresh(bot)

    # Inicializa os saldos lógicos do bot (reserved_amount por moeda)
    initialize_bot_balances(bot_id=bot.id)

    return bot
# ==== BLOCK: ROUTES_BOTS_ACTIVATE - END ====


# ==== BLOCK: ROUTES_BOTS_DEACTIVATE - START ====
@router.patch("/{bot_id}/deactivate", response_model=Bot)
def deactivate_bot(bot_id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")

    if not bot.is_active:
        # Já está desligado, nada a fazer
        return bot

    # Marca como inativo
    bot.is_active = False

    # "Desbloqueia" recursos reservados: zera o reserved_amount de todas as moedas do bot.
    stmt_assets = select(BotAsset).where(BotAsset.bot_id == bot_id)
    assets = session.exec(stmt_assets).all()
    for asset in assets:
        asset.reserved_amount = 0.0
        session.add(asset)

    session.add(bot)
    session.commit()
    session.refresh(bot)

    return bot
# ==== BLOCK: ROUTES_BOTS_DEACTIVATE - END ====


# ==== BLOCK: ROUTES_BOTS_UPDATE - START ====
@router.patch("/{bot_id}", response_model=Bot)
def update_bot(
    bot_id: int,
    data: BotUpdate,
    session: Session = Depends(get_session),
):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")

    # Atualiza somente os campos enviados
    if data.name is not None:
        bot.name = data.name

    if data.initial_balance_usdt is not None:
        bot.initial_balance_usdt = float(data.initial_balance_usdt)

    if data.stop_loss_percent is not None:
        bot.stop_loss_percent = float(data.stop_loss_percent)

    if data.stop_behavior is not None:
        bot.stop_behavior = data.stop_behavior

    session.add(bot)
    session.commit()
    session.refresh(bot)
    return bot
# ==== BLOCK: ROUTES_BOTS_UPDATE - END ====


# ==== BLOCK: ROUTE_BOT_TRADE_MODE - START ====
from pydantic import BaseModel

class BotTradeModeUpdate(BaseModel):
    trade_mode: str  # "REAL" ou "SIMULATED"

@router.patch("/{bot_id}/trade-mode")
def update_trade_mode(
    bot_id: int,
    payload: BotTradeModeUpdate,
    session: Session = Depends(get_session)
):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")

    new_mode = payload.trade_mode.upper()

    if new_mode not in ("REAL", "SIMULATED"):
        raise HTTPException(
            status_code=400,
            detail="trade_mode deve ser REAL ou SIMULATED."
        )

    bot.trade_mode = new_mode
    bot.updated_at = datetime.utcnow()

    session.add(bot)
    session.commit()
    session.refresh(bot)

    return bot
# ==== BLOCK: ROUTE_BOT_TRADE_MODE - END ====

