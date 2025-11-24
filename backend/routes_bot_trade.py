# ============================================================
# backend/routes_bot_trade.py — VERSÃO ALINHADA AO NOVO CLIENTE
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from .db import get_session
from .models import Bot, BotAsset, BotLog
from .binance_client import (
    get_symbol_price_usdt,
    get_symbol_filters,
    adjust_quantity_to_filters,
    create_market_sell_order,
    create_market_buy_order,
    get_account_balance,
)

router = APIRouter()


# ============================================================
# MODELOS DE REQUISIÇÃO
# ============================================================

class MarketSwapRequest(BaseModel):
    sell_symbol: str
    buy_symbol: str
    trade_unit_usdt: float = 10.0


# ============================================================
# HELPERS
# ============================================================

def _get_bot_or_404(session: Session, bot_id: int) -> Bot:
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")
    return bot


def _get_asset_or_404(session: Session, bot_id: int, symbol: str) -> BotAsset:
    symbol = symbol.upper()
    stmt = select(BotAsset).where(
        BotAsset.bot_id == bot_id,
        BotAsset.symbol == symbol,
    )
    asset = session.exec(stmt).first()
    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Moeda {symbol} não está configurada neste bot."
        )
    return asset


# ============================================================
# LÓGICA PRINCIPAL DE SWAP REAL VIA USDT (SPOT MARKET)
# ============================================================

def _execute_spot_market_swap_via_usdt(
    session: Session,
    bot_id: int,
    sell_symbol: str,
    buy_symbol: str,
    trade_unit_usdt: float,
):
    sell_symbol = sell_symbol.upper()
    buy_symbol = buy_symbol.upper()

    bot = _get_bot_or_404(session, bot_id)

    if not bot.is_active:
        raise HTTPException(
            status_code=400,
            detail="Bot precisa estar ativo para executar trades reais."
        )

    if sell_symbol == buy_symbol:
        raise HTTPException(
            status_code=400,
            detail="sell_symbol e buy_symbol não podem ser iguais."
        )

    sell_asset = _get_asset_or_404(session, bot_id, sell_symbol)
    buy_asset = _get_asset_or_404(session, bot_id, buy_symbol)

    # Preços atuais em USDT
    sell_price_usdt = get_symbol_price_usdt(sell_symbol)
    buy_price_usdt = get_symbol_price_usdt(buy_symbol)

    # Quantidade a vender para aproximadamente trade_unit_usdt
    raw_amount_sell = trade_unit_usdt / sell_price_usdt

    # Ajustar pela LOT_SIZE da Binance
    amount_sell = adjust_quantity_to_filters(sell_symbol, raw_amount_sell)

    if amount_sell <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantidade calculada para venda é zero ou negativa após ajustes de LOT_SIZE."
        )

    # Verificar saldo REAL em carteira (fora do conceito de saldo reservado do bot)
    available_balance = get_account_balance(sell_symbol)
    if available_balance < amount_sell:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente em {sell_symbol} na sua conta Binance. "
                   f"Disponível: {available_balance:.8f}, Necessário: {amount_sell:.8f}."
        )

    # --------------------------------------------------------
    # 1) Enviar ORDEM MARKET SELL (sell_symbol -> USDT)
    # --------------------------------------------------------
    try:
        sell_order = create_market_sell_order(sell_symbol, amount_sell)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao enviar ordem MARKET SELL para {sell_symbol}USDT: {e}"
        )

    # Tentar obter quanto de USDT entrou de fato
    usdt_from_sell = None
    if "cummulativeQuoteQty" in sell_order:
        try:
            usdt_from_sell = float(sell_order["cummulativeQuoteQty"])
        except Exception:
            usdt_from_sell = None

    if not usdt_from_sell:
        # fallback aproximado
        usdt_from_sell = amount_sell * sell_price_usdt

    # --------------------------------------------------------
    # 2) Enviar ORDEM MARKET BUY (USDT -> buy_symbol)
    # --------------------------------------------------------
    try:
        buy_order = create_market_buy_order(buy_symbol, usdt_from_sell)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao enviar ordem MARKET BUY para {buy_symbol}USDT: {e}"
        )

    amount_bought = 0.0
    if "executedQty" in buy_order:
        try:
            amount_bought = float(buy_order["executedQty"])
        except Exception:
            amount_bought = 0.0

    # Atualizar "saldo" interno do bot e logs
    # OBS: aqui não estamos gerindo o saldo reservado por moeda,
    # apenas registrando o swap e deixando o saldo real na Binance
    # ser o source of truth para posições.
    message = (
        f"SWAP REAL: vende {amount_sell:.8f} {sell_symbol} "
        f"e compra {amount_bought:.8f} {buy_symbol} "
        f"(~{trade_unit_usdt:.2f} USDT)."
    )

    log = BotLog(
        bot_id=bot_id,
        side="REAL_SWAP",
        from_symbol=sell_symbol,
        to_symbol=buy_symbol,
        amount_from=amount_sell,
        amount_to=amount_bought,
        price_usdt=sell_price_usdt,
        message=message,
    )
    session.add(log)
    session.commit()
    session.refresh(log)

    return {
        "executed": True,
        "message": message,
        "bot_id": bot_id,
        "bot_name": bot.name,
        "sell_symbol": sell_symbol,
        "buy_symbol": buy_symbol,
        "sell_price_usdt": sell_price_usdt,
        "buy_price_usdt": buy_price_usdt,
        "amount_sold": amount_sell,
        "amount_bought": amount_bought,
        "log_id": log.id,
    }


# ============================================================
# ENDPOINT: SWAP REAL MARKET (SPOT)
# ============================================================

@router.post("/api/bots/{bot_id}/trade/market-swap/")
def post_market_swap(
    bot_id: int,
    body: MarketSwapRequest,
    session: Session = Depends(get_session),
):
    """
    Executa um SWAP REAL via mercado spot:
    - SELL: {sell_symbol}USDT
    - BUY:  {buy_symbol}USDT
    Ambos usando ordens MARKET.
    """
    return _execute_spot_market_swap_via_usdt(
        session=session,
        bot_id=bot_id,
        sell_symbol=body.sell_symbol,
        buy_symbol=body.buy_symbol,
        trade_unit_usdt=body.trade_unit_usdt,
    )
