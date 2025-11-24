# ============================================================
# backend/routes_trade_logs.py — VERSÃO CORRIGIDA
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from .db import get_session
from .models import Bot, BotLog

router = APIRouter()


# ============================================================
# LISTAR LOGS DE UM BOT
# ============================================================

@router.get("/api/bots/{bot_id}/logs/")
def list_bot_logs(bot_id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")

    statement = (
        select(BotLog)
        .where(BotLog.bot_id == bot_id)
        .order_by(BotLog.created_at.desc())
    )

    logs = session.exec(statement).all()
    return logs


# ============================================================
# OBTER DETALHES DE UM LOG ESPECÍFICO
# ============================================================

@router.get("/api/logs/{log_id}")
def get_log_details(log_id: int, session: Session = Depends(get_session)):
    log = session.get(BotLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log não encontrado.")

    return log
