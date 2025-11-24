# ==== BLOCK: ROUTES_BOT_ANALYSIS_IMPORTS - START ====
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from .db import get_session
from .models import Bot, BotAsset
from .binance_client import get_symbol_price_usdt
# ==== BLOCK: ROUTES_BOT_ANALYSIS_IMPORTS - END ====


# ==== BLOCK: ROUTES_BOT_ANALYSIS_ROUTER - START ====
router = APIRouter(prefix="/api/bots/{bot_id}/analysis", tags=["bot-analysis"])
# ==== BLOCK: ROUTES_BOT_ANALYSIS_ROUTER - END ====


# ==== BLOCK: ROUTES_BOT_ANALYSIS_SCHEMAS - START ====
class AssetAnalysis(BaseModel):
    symbol: str
    initial_price_usdt: float
    current_price_usdt: float
    change_percent: float
    can_buy_now: bool
    can_sell_now: bool
    buy_threshold_percent: float
    sell_threshold_percent: float
    can_buy_flag: bool
    can_sell_flag: bool


class BotAnalysisResponse(BaseModel):
    bot_id: int
    bot_name: str
    assets: List[AssetAnalysis]
    buy_candidates: List[str]
    sell_candidates: List[str]
# ==== BLOCK: ROUTES_BOT_ANALYSIS_SCHEMAS - END ====


# ==== BLOCK: ROUTES_BOT_ANALYSIS_GET - START ====
@router.get("/", response_model=BotAnalysisResponse)
def analyze_bot(bot_id: int, session: Session = Depends(get_session)):
    # 1) Verifica se o bot existe
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")

    # 2) Carrega as moedas do bot
    stmt_assets = select(BotAsset).where(BotAsset.bot_id == bot_id)
    assets = session.exec(stmt_assets).all()
    if not assets:
        raise HTTPException(
            status_code=400,
            detail="Nenhuma moeda configurada para este bot.",
        )

    analysis_items: List[AssetAnalysis] = []
    buy_candidates: List[str] = []
    sell_candidates: List[str] = []

    for asset in assets:
        initial_price = asset.initial_price_usdt or 0.0
        if initial_price <= 0:
            # Sem preço inicial válido não dá pra analisar variação
            current_price = 0.0
            change_percent = 0.0
        else:
            # Busca preço atual na Binance
            current_price = get_symbol_price_usdt(asset.symbol) or 0.0
            if current_price <= 0:
                change_percent = 0.0
            else:
                change_percent = ((current_price - initial_price) / initial_price) * 100.0

        # Regras de compra/venda:
        # - buy_percent: ex. -5 => queremos comprar quando change_percent <= -5
        # - sell_percent: ex. +10 => queremos vender quando change_percent >= 10
        # Só consideramos se as flags can_buy / can_sell estiverem ativas.

        can_buy_now = (
            asset.can_buy
            and initial_price > 0
            and current_price > 0
            and change_percent <= asset.buy_percent
        )

        can_sell_now = (
            asset.can_sell
            and initial_price > 0
            and current_price > 0
            and change_percent >= asset.sell_percent
        )

        if can_buy_now:
            buy_candidates.append(asset.symbol)

        if can_sell_now:
            sell_candidates.append(asset.symbol)

        analysis_items.append(
            AssetAnalysis(
                symbol=asset.symbol,
                initial_price_usdt=initial_price,
                current_price_usdt=current_price,
                change_percent=change_percent,
                can_buy_now=can_buy_now,
                can_sell_now=can_sell_now,
                buy_threshold_percent=asset.buy_percent,
                sell_threshold_percent=asset.sell_percent,
                can_buy_flag=asset.can_buy,
                can_sell_flag=asset.can_sell,
            )
        )

    return BotAnalysisResponse(
        bot_id=bot.id,
        bot_name=bot.name,
        assets=analysis_items,
        buy_candidates=buy_candidates,
        sell_candidates=sell_candidates,
    )
# ==== BLOCK: ROUTES_BOT_ANALYSIS_GET - END ====
