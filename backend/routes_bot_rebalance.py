# ==== BLOCK: ROUTES_BOT_REBALANCE_IMPORTS - START ====
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from .db import get_session
from .models import Bot
from .bot_rebalance import rebalance_bot, RebalancedAsset, RebalanceResult
# ==== BLOCK: ROUTES_BOT_REBALANCE_IMPORTS - END ====


# ==== BLOCK: ROUTES_BOT_REBALANCE_ROUTER - START ====
router = APIRouter(
    prefix="/api/bots/{bot_id}/rebalance",
    tags=["bot-rebalance"],
)
# ==== BLOCK: ROUTES_BOT_REBALANCE_ROUTER - END ====


# ==== BLOCK: ROUTES_BOT_REBALANCE_SCHEMAS - START ====
class RebalancedAssetOut(BaseModel):
    symbol: str
    old_reserved: float
    new_reserved: float
    old_value_usdt: float
    new_value_usdt: float


class RebalanceResponse(BaseModel):
    bot_id: int
    bot_name: str
    target_per_asset_usdt: float
    total_value_before: float
    total_value_after: float
    insufficient_funds: bool
    assets: List[RebalancedAssetOut]
# ==== BLOCK: ROUTES_BOT_REBALANCE_SCHEMAS - END ====


# ==== BLOCK: ROUTES_BOT_REBALANCE_POST - START ====
@router.post("/", response_model=RebalanceResponse)
def do_rebalance(bot_id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")

    # Usa o valor padrão de 10 USDT por moeda (pode virar config por bot depois)
    result: RebalanceResult = rebalance_bot(bot_id=bot_id, target_per_asset_usdt=10.0)

    return RebalanceResponse(
        bot_id=result.bot_id,
        bot_name=result.bot_name,
        target_per_asset_usdt=result.target_per_asset_usdt,
        total_value_before=result.total_value_before,
        total_value_after=result.total_value_after,
        insufficient_funds=result.insufficient_funds,
        assets=[
            RebalancedAssetOut(
                symbol=a.symbol,
                old_reserved=a.old_reserved,
                new_reserved=a.new_reserved,
                old_value_usdt=a.old_value_usdt,
                new_value_usdt=a.new_value_usdt,
            )
            for a in result.assets
        ],
    )
# ==== BLOCK: ROUTES_BOT_REBALANCE_POST - END ====
