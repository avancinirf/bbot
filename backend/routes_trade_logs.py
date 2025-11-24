# ==== BLOCK: ROUTES_TRADE_LOGS_IMPORTS - START ====
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from .db import get_session
from .models import Bot, TradeLog
# ==== BLOCK: ROUTES_TRADE_LOGS_IMPORTS - END ====


# ==== BLOCK: ROUTES_TRADE_LOGS_ROUTER - START ====
router = APIRouter(prefix="/api/bots/{bot_id}/logs", tags=["bot-logs"])
# ==== BLOCK: ROUTES_TRADE_LOGS_ROUTER - END ====


# ==== BLOCK: ROUTES_TRADE_LOGS_SCHEMAS - START ====
class TradeLogCreate(BaseModel):
    from_symbol: str
    to_symbol: str
    side: str = "SWAP"
    amount_from: float
    amount_to: float
    price_usdt: float
    message: str | None = None
# ==== BLOCK: ROUTES_TRADE_LOGS_SCHEMAS - END ====


# ==== BLOCK: ROUTES_TRADE_LOGS_LIST - START ====
@router.get("/", response_model=List[TradeLog])
def list_logs(bot_id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")

    statement = (
        select(TradeLog)
        .where(TradeLog.bot_id == bot_id)
        .order_by(TradeLog.created_at.desc())
    )
    logs = session.exec(statement).all()
    return logs
# ==== BLOCK: ROUTES_TRADE_LOGS_LIST - END ====


# ==== BLOCK: ROUTES_TRADE_LOGS_CREATE - START ====
@router.post("/", response_model=TradeLog)
def create_log(
    bot_id: int,
    log_data: TradeLogCreate,
    session: Session = Depends(get_session),
):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")

    db_log = TradeLog(
        bot_id=bot_id,
        from_symbol=log_data.from_symbol.upper(),
        to_symbol=log_data.to_symbol.upper(),
        side=log_data.side.upper(),
        amount_from=log_data.amount_from,
        amount_to=log_data.amount_to,
        price_usdt=log_data.price_usdt,
        message=log_data.message,
    )

    session.add(db_log)
    session.commit()
    session.refresh(db_log)
    return db_log
# ==== BLOCK: ROUTES_TRADE_LOGS_CREATE - END ====
