# ==== BLOCK: ROUTES_BOT_INDICATORS_IMPORTS - START ====
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from .db import get_session
from .models import Bot, BotAsset
from .indicators import build_indicators_for_symbol
# ==== BLOCK: ROUTES_BOT_INDICATORS_IMPORTS - END ====


# ==== BLOCK: ROUTES_BOT_INDICATORS_ROUTER - START ====
router = APIRouter(
    prefix="/api/bots/{bot_id}/indicators",
    tags=["bot-indicators"],
)
# ==== BLOCK: ROUTES_BOT_INDICATORS_ROUTER - END ====


# ==== BLOCK: ROUTES_BOT_INDICATORS_SCHEMAS - START ====
class SymbolIndicatorsOut(BaseModel):
    symbol: str
    price_usdt: Optional[float]
    rsi_14: Optional[float]
    ema_fast: Optional[float]
    ema_slow: Optional[float]
    trend: Optional[str]
    initial_price_usdt: float
    change_percent: Optional[float]


class BotIndicatorsResponse(BaseModel):
    bot_id: int
    bot_name: str
    generated_at: datetime
    assets: List[SymbolIndicatorsOut]
# ==== BLOCK: ROUTES_BOT_INDICATORS_SCHEMAS - END ====


# ==== BLOCK: ROUTES_BOT_INDICATORS_GET - START ====
@router.get("/", response_model=BotIndicatorsResponse)
def get_bot_indicators(
    bot_id: int,
    session: Session = Depends(get_session),
):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")

    stmt_assets = select(BotAsset).where(BotAsset.bot_id == bot_id)
    assets = session.exec(stmt_assets).all()

    indicators_out: list[SymbolIndicatorsOut] = []

    for asset in assets:
        ind = build_indicators_for_symbol(asset.symbol)

        change_percent: Optional[float] = None
        if asset.initial_price_usdt and ind.price_usdt:
            change_percent = (
                (ind.price_usdt - asset.initial_price_usdt)
                / asset.initial_price_usdt
                * 100.0
            )

        indicators_out.append(
            SymbolIndicatorsOut(
                symbol=asset.symbol,
                price_usdt=ind.price_usdt,
                rsi_14=ind.rsi_14,
                ema_fast=ind.ema_fast,
                ema_slow=ind.ema_slow,
                trend=ind.trend,
                initial_price_usdt=asset.initial_price_usdt,
                change_percent=change_percent,
            )
        )

    return BotIndicatorsResponse(
        bot_id=bot.id,
        bot_name=bot.name,
        generated_at=datetime.utcnow(),
        assets=indicators_out,
    )
# ==== BLOCK: ROUTES_BOT_INDICATORS_GET - END ====
