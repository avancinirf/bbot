# ==== BLOCK: ROUTES_BOT_SIMTRADE_IMPORTS - START ====
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from .db import get_session
from .models import Bot, BotAsset, TradeLog
from .binance_client import get_symbol_price_usdt
# ==== BLOCK: ROUTES_BOT_SIMTRADE_IMPORTS - END ====


# ==== BLOCK: ROUTES_BOT_SIMTRADE_ROUTER - START ====
router = APIRouter(
    prefix="/api/bots/{bot_id}/simulate-trade", tags=["bot-simulated-trade"]
)
# ==== BLOCK: ROUTES_BOT_SIMTRADE_ROUTER - END ====


# ==== BLOCK: ROUTES_BOT_SIMTRADE_SCHEMAS - START ====
class SimulatedTradeResult(BaseModel):
    bot_id: int
    bot_name: str
    executed: bool
    message: str

    trade_unit_usdt: float

    sell_symbol: Optional[str] = None
    buy_symbol: Optional[str] = None

    sell_price_usdt: Optional[float] = None
    buy_price_usdt: Optional[float] = None

    amount_from: Optional[float] = None  # quantidade da moeda vendida
    amount_to: Optional[float] = None    # quantidade da moeda comprada

    log_id: Optional[int] = None
# ==== BLOCK: ROUTES_BOT_SIMTRADE_SCHEMAS - END ====


# ==== BLOCK: ROUTES_BOT_SIMTRADE_POST - START ====
@router.post("/", response_model=SimulatedTradeResult)
def simulate_trade(bot_id: int, session: Session = Depends(get_session)):
    TRADE_UNIT_USDT = 10.0

    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")

    # Carrega as moedas do bot
    stmt_assets = select(BotAsset).where(BotAsset.bot_id == bot_id)
    assets = session.exec(stmt_assets).all()
    if not assets:
        return SimulatedTradeResult(
            bot_id=bot.id,
            bot_name=bot.name,
            executed=False,
            message="Nenhuma moeda configurada para este bot.",
            trade_unit_usdt=TRADE_UNIT_USDT,
        )

    sell_candidates = []
    buy_candidates = []
    asset_by_symbol = {a.symbol.upper(): a for a in assets}

    for asset in assets:
        initial_price = asset.initial_price_usdt or 0.0
        if initial_price <= 0:
            continue

        current_price = get_symbol_price_usdt(asset.symbol) or 0.0
        if current_price <= 0:
            continue

        change_percent = ((current_price - initial_price) / initial_price) * 100.0
        reserved_value_usdt = asset.reserved_amount * current_price

        # Candidata para COMPRA?
        if asset.can_buy and change_percent <= asset.buy_percent:
            buy_candidates.append((asset.symbol, change_percent))

        # Candidata para VENDA? exige saldo reservado >= TRADE_UNIT_USDT
        if (
            asset.can_sell
            and change_percent >= asset.sell_percent
            and reserved_value_usdt >= TRADE_UNIT_USDT
        ):
            sell_candidates.append((asset.symbol, change_percent))

    if not sell_candidates or not buy_candidates:
        return SimulatedTradeResult(
            bot_id=bot.id,
            bot_name=bot.name,
            executed=False,
            message=(
                "Ainda não há combinação de moedas em zona de venda e compra ao mesmo tempo "
                "com saldo reservado suficiente. Nenhum trade simulado foi executado."
            ),
            trade_unit_usdt=TRADE_UNIT_USDT,
        )

    # Escolhe a moeda a vender e a comprar
    sell_symbol, sell_change = max(sell_candidates, key=lambda item: item[1])
    buy_symbol, buy_change = min(buy_candidates, key=lambda item: item[1])

    sell_symbol = sell_symbol.upper()
    buy_symbol = buy_symbol.upper()

    if sell_symbol == buy_symbol:
        return SimulatedTradeResult(
            bot_id=bot.id,
            bot_name=bot.name,
            executed=False,
            message=(
                "Moeda candidata para compra e venda é a mesma. "
                "Nenhum trade simulado foi executado."
            ),
            trade_unit_usdt=TRADE_UNIT_USDT,
        )

    sell_asset = asset_by_symbol.get(sell_symbol)
    buy_asset = asset_by_symbol.get(buy_symbol)

    if sell_asset is None or buy_asset is None:
        return SimulatedTradeResult(
            bot_id=bot.id,
            bot_name=bot.name,
            executed=False,
            message="Erro interno: não foi possível localizar os assets no bot.",
            trade_unit_usdt=TRADE_UNIT_USDT,
        )

    # Preços atuais para o trade
    sell_price = get_symbol_price_usdt(sell_symbol) or 0.0
    buy_price = get_symbol_price_usdt(buy_symbol) or 0.0

    if sell_price <= 0 or buy_price <= 0:
        return SimulatedTradeResult(
            bot_id=bot.id,
            bot_name=bot.name,
            executed=False,
            message="Não foi possível obter preços atuais válidos para as moedas.",
            trade_unit_usdt=TRADE_UNIT_USDT,
        )

    # Quantidade da moeda vendida equivalente a 10 USDT
    amount_from = TRADE_UNIT_USDT / sell_price

    # Verifica se o bot tem saldo lógico suficiente dessa moeda
    if sell_asset.reserved_amount < amount_from:
        return SimulatedTradeResult(
            bot_id=bot.id,
            bot_name=bot.name,
            executed=False,
            message=(
                f"Saldo reservado insuficiente em {sell_symbol} para simular venda de "
                f"{TRADE_UNIT_USDT} USDT. "
                f"Reservado: {sell_asset.reserved_amount:.8f}, "
                f"Necessário: {amount_from:.8f}."
            ),
            trade_unit_usdt=TRADE_UNIT_USDT,
        )

    # Quantidade da moeda comprada com 10 USDT
    amount_to = TRADE_UNIT_USDT / buy_price

    # Atualiza saldos lógicos (reserved_amount)
    sell_asset.reserved_amount -= amount_from
    buy_asset.reserved_amount += amount_to

    # Atualiza preço inicial das duas moedas para o novo preço (nova âncora)
    now = datetime.utcnow()
    sell_asset.initial_price_usdt = sell_price
    sell_asset.updated_at = now

    buy_asset.initial_price_usdt = buy_price
    buy_asset.updated_at = now

    session.add(sell_asset)
    session.add(buy_asset)
    session.commit()
    session.refresh(sell_asset)
    session.refresh(buy_asset)

    # Cria o log da operação simulada
    log = TradeLog(
        bot_id=bot.id,
        from_symbol=sell_symbol,
        to_symbol=buy_symbol,
        side="SIMULATED_SWAP",
        amount_from=amount_from,
        amount_to=amount_to,
        price_usdt=sell_price,
        message=(
            f"Trade SIMULADO: vende {sell_symbol} (~{TRADE_UNIT_USDT} USDT) "
            f"e compra {buy_symbol} (~{TRADE_UNIT_USDT} USDT)."
        ),
    )
    session.add(log)
    session.commit()
    session.refresh(log)

    msg = (
        f"Trade simulado executado: vende {sell_symbol} "
        f"(~{TRADE_UNIT_USDT} USDT) e compra {buy_symbol} "
        f"(~{TRADE_UNIT_USDT} USDT)."
    )

    return SimulatedTradeResult(
        bot_id=bot.id,
        bot_name=bot.name,
        executed=True,
        message=msg,
        trade_unit_usdt=TRADE_UNIT_USDT,
        sell_symbol=sell_symbol,
        buy_symbol=buy_symbol,
        sell_price_usdt=sell_price,
        buy_price_usdt=buy_price,
        amount_from=amount_from,
        amount_to=amount_to,
        log_id=log.id,
    )
# ==== BLOCK: ROUTES_BOT_SIMTRADE_POST - END ====
