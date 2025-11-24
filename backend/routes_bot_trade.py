# ==== BLOCK: ROUTES_BOT_TRADE_IMPORTS - START ====
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from .db import get_session
from .models import Bot, BotAsset, BotLog
from .binance_client import (
    get_spot_client,
    get_symbol_price_usdt,
    adjust_quantity_to_filters,
    adjust_quote_to_min_notional,
)
# ==== BLOCK: ROUTES_BOT_TRADE_IMPORTS - END ====


# ==== BLOCK: ROUTES_BOT_TRADE_ROUTER - START ====
router = APIRouter(
    prefix="/api/bots/{bot_id}/trade",
    tags=["bot-trade"],
)
# ==== BLOCK: ROUTES_BOT_TRADE_ROUTER - END ====


# ==== BLOCK: ROUTES_BOT_TRADE_SCHEMAS - START ====
class MarketSwapRequest(BaseModel):
    sell_symbol: str = Field(..., description="Moeda que será vendida (ex: XRP)")
    buy_symbol: str = Field(..., description="Moeda que será comprada (ex: SOL)")
    trade_unit_usdt: float = Field(
        10.0, description="Valor alvo em USDT para a operação.", gt=0
    )


class MarketSwapResponse(BaseModel):
    executed: bool
    message: str

    bot_id: int
    bot_name: str

    sell_symbol: Optional[str] = None
    buy_symbol: Optional[str] = None

    sell_price_usdt: Optional[float] = None
    buy_price_usdt: Optional[float] = None

    amount_sold: Optional[float] = None
    amount_bought: Optional[float] = None

    log_id: Optional[int] = None
# ==== BLOCK: ROUTES_BOT_TRADE_SCHEMAS - END ====


# ==== BLOCK: ROUTES_BOT_TRADE_EXECUTOR - START ====
def _execute_spot_market_swap_via_usdt(
    *,
    bot: Bot,
    sell_asset: BotAsset,
    buy_asset: BotAsset,
    trade_unit_usdt: float,
    session: Session,
) -> MarketSwapResponse:

    client = get_spot_client()

    sell_symbol = sell_asset.symbol.upper()
    buy_symbol = buy_asset.symbol.upper()

    if sell_symbol == buy_symbol:
        return MarketSwapResponse(
            executed=False,
            message="As moedas de venda e compra não podem ser iguais.",
            bot_id=bot.id,
            bot_name=bot.name,
        )

    # 1) Preço atual
    sell_price = get_symbol_price_usdt(sell_symbol)
    buy_price = get_symbol_price_usdt(buy_symbol)

    if sell_price is None or buy_price is None:
        return MarketSwapResponse(
            executed=False,
            message="Não foi possível obter preços na Binance.",
            bot_id=bot.id,
            bot_name=bot.name,
            sell_symbol=sell_symbol,
            buy_symbol=buy_symbol,
        )

    # 2) Calcula quantidade aproximada
    amount_sell = trade_unit_usdt / sell_price

    # Nunca vender mais do que o reservado
    if sell_asset.reserved_amount < amount_sell:
        amount_sell = sell_asset.reserved_amount

    # 3) Ajusta LOT_SIZE
    amount_sell = adjust_quantity_to_filters(sell_symbol, amount_sell)

    if amount_sell <= 0:
        return MarketSwapResponse(
            executed=False,
            message=(
                f"Quantidade inválida para vender {sell_symbol}. "
                f"O LOT_SIZE exige valor maior."
            ),
            bot_id=bot.id,
            bot_name=bot.name,
        )

    pair_sell = f"{sell_symbol}USDT"
    pair_buy = f"{buy_symbol}USDT"

    # 4) Ordem MARKET SELL
    try:
        sell_order = client.new_order(
            symbol=pair_sell,
            side="SELL",
            type="MARKET",
            quantity=amount_sell,
        )
    except Exception as e:
        return MarketSwapResponse(
            executed=False,
            message=f"Erro ao enviar ordem MARKET SELL para {pair_sell}: {e}",
            bot_id=bot.id,
            bot_name=bot.name,
            sell_symbol=sell_symbol,
            buy_symbol=buy_symbol,
        )

    # Extrai execução
    executed_qty_sell = float(sell_order.get("executedQty", 0))
    usdt_obtido = float(sell_order.get("cummulativeQuoteQty", 0))

    if executed_qty_sell <= 0 or usdt_obtido <= 0:
        return MarketSwapResponse(
            executed=False,
            message="Venda executou quantidade insuficiente.",
            bot_id=bot.id,
            bot_name=bot.name,
        )

    # 5) Ajusta NOTIONAL da compra
    usdt_obtido = adjust_quote_to_min_notional(buy_symbol, usdt_obtido)
    if usdt_obtido <= 0:
        return MarketSwapResponse(
            executed=False,
            message=(
                f"USDT obtido insuficiente para comprar {buy_symbol} "
                f"(MIN_NOTIONAL da Binance)."
            ),
            bot_id=bot.id,
            bot_name=bot.name,
        )

    # 6) Ordem MARKET BUY
    try:
        buy_order = client.new_order(
            symbol=pair_buy,
            side="BUY",
            type="MARKET",
            quoteOrderQty=usdt_obtido,
        )
    except Exception as e:
        return MarketSwapResponse(
            executed=False,
            message=f"Erro ao enviar ordem MARKET BUY para {pair_buy}: {e}",
            bot_id=bot.id,
            bot_name=bot.name,
        )

    executed_qty_buy = float(buy_order.get("executedQty", 0))

    if executed_qty_buy <= 0:
        return MarketSwapResponse(
            executed=False,
            message="Compra não executou quantidade suficiente.",
            bot_id=bot.id,
            bot_name=bot.name,
        )

    # 7) Atualiza saldos no BOT
    sell_asset.reserved_amount -= executed_qty_sell
    if sell_asset.reserved_amount < 0:
        sell_asset.reserved_amount = 0

    buy_asset.reserved_amount += executed_qty_buy

    sell_asset.initial_price_usdt = sell_price
    buy_asset.initial_price_usdt = buy_price

    session.add(sell_asset)
    session.add(buy_asset)

    # 8) Registra trade log
    log = BotLog(
        bot_id=bot.id,
        side="SWAP",
        from_symbol=sell_symbol,
        to_symbol=buy_symbol,
        amount_from=executed_qty_sell,
        amount_to=executed_qty_buy,
        price_usdt=sell_price,
        message=(
            f"SWAP REAL: vende {executed_qty_sell:.8f} {sell_symbol} "
            f"e compra {executed_qty_buy:.8f} {buy_symbol}."
        ),
    )
    session.add(log)
    session.commit()
    session.refresh(log)

    return MarketSwapResponse(
        executed=True,
        message=log.message,
        bot_id=bot.id,
        bot_name=bot.name,
        sell_symbol=sell_symbol,
        buy_symbol=buy_symbol,
        sell_price_usdt=sell_price,
        buy_price_usdt=buy_price,
        amount_sold=executed_qty_sell,
        amount_bought=executed_qty_buy,
        log_id=log.id,
    )
# ==== BLOCK: ROUTES_BOT_TRADE_EXECUTOR - END ====


# ==== BLOCK: ROUTES_BOT_TRADE_ENDPOINT - START ====
@router.post("/market-swap/", response_model=MarketSwapResponse)
def post_market_swap(
    bot_id: int,
    payload: MarketSwapRequest,
    session: Session = Depends(get_session),
):

    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(404, "Bot não encontrado.")

    if not bot.is_active:
        raise HTTPException(400, "Bot deve estar ativo para trade real.")

    sell_symbol = payload.sell_symbol.upper()
    buy_symbol = payload.buy_symbol.upper()

    # Seleciona ativos do bot
    assets = session.exec(select(BotAsset).where(BotAsset.bot_id == bot_id)).all()
    sell_asset = next((a for a in assets if a.symbol.upper() == sell_symbol), None)
    buy_asset = next((a for a in assets if a.symbol.upper() == buy_symbol), None)

    if not sell_asset:
        raise HTTPException(400, f"{sell_symbol} não está configurada no bot.")
    if not buy_asset:
        raise HTTPException(400, f"{buy_symbol} não está configurada no bot.")

    if not sell_asset.can_sell:
        raise HTTPException(400, f"{sell_symbol} está com venda desativada.")
    if not buy_asset.can_buy:
        raise HTTPException(400, f"{buy_symbol} está com compra desativada.")

    return _execute_spot_market_swap_via_usdt(
        bot=bot,
        sell_asset=sell_asset,
        buy_asset=buy_asset,
        trade_unit_usdt=payload.trade_unit_usdt,
        session=session,
    )
# ==== BLOCK: ROUTES_BOT_TRADE_ENDPOINT - END ====
