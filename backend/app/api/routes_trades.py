from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import Trade

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("/ping")
def trades_ping() -> dict:
  return {"message": "trades endpoint ok"}


@router.get("/recent")
def list_recent_trades(
  limit: int = Query(50, ge=1, le=500),
  bot_id: Optional[int] = None,
  symbol: Optional[str] = None,
  session: Session = Depends(get_session),
) -> List[Trade]:
  """
  Lista os trades mais recentes, opcionalmente filtrando por bot_id e/ou symbol.
  Ordena do mais recente para o mais antigo.
  """
  query = select(Trade)

  if bot_id is not None:
    query = query.where(Trade.bot_id == bot_id)

  if symbol is not None:
    symbol = symbol.upper().strip()
    query = query.where(Trade.symbol == symbol)

  # mais recentes primeiro
  query = query.order_by(Trade.id.desc()).limit(limit)

  trades = session.exec(query).all()
  return trades
