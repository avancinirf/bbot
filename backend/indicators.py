# ==== BLOCK: INDICATORS_IMPORTS - START ====
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .binance_client import get_symbol_price_usdt, get_symbol_klines
# ==== BLOCK: INDICATORS_IMPORTS - END ====


# ==== BLOCK: INDICATORS_MODELS - START ====
@dataclass
class SymbolIndicators:
    symbol: str
    price_usdt: Optional[float]
    rsi_14: Optional[float]
    ema_fast: Optional[float]
    ema_slow: Optional[float]
    trend: Optional[str]
# ==== BLOCK: INDICATORS_MODELS - END ====


# ==== BLOCK: INDICATORS_CALCS - START ====
def _ema(values: List[float], period: int) -> Optional[float]:
    if not values or len(values) < period:
        return None

    k = 2 / (period + 1)
    ema_value = values[0]
    for price in values[1:]:
        ema_value = price * k + ema_value * (1 - k)
    return ema_value


def _rsi(values: List[float], period: int = 14) -> Optional[float]:
    if not values or len(values) < period + 1:
        return None

    gains: List[float] = []
    losses: List[float] = []

    for i in range(1, len(values)):
        delta = values[i] - values[i - 1]
        if delta > 0:
            gains.append(delta)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(-delta)

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi_value = 100 - (100 / (1 + rs))
    return rsi_value
# ==== BLOCK: INDICATORS_CALCS - END ====


# ==== BLOCK: INDICATORS_BUILD - START ====
def build_indicators_for_symbol(
    symbol: str,
    interval: str = "15m",
    limit: int = 100,
) -> SymbolIndicators:
    """
    Calcula indicadores básicos para uma moeda:
    - preço atual em USDT
    - RSI(14)
    - EMA rápida (9)
    - EMA lenta (21)
    - tendência básica (UP / DOWN / FLAT)
    """
    klines = get_symbol_klines(symbol, interval=interval, limit=limit)
    closes = [k["close"] for k in klines] if klines else []

    price = get_symbol_price_usdt(symbol)

    ema_fast = _ema(closes, period=9) if closes else None
    ema_slow = _ema(closes, period=21) if closes else None
    rsi_14 = _rsi(closes, period=14) if closes else None

    trend: Optional[str] = None
    if ema_fast is not None and ema_slow is not None:
        if abs(ema_fast - ema_slow) < (price or ema_fast) * 0.0005:
            trend = "FLAT"
        elif ema_fast > ema_slow:
            trend = "UP"
        else:
            trend = "DOWN"

    return SymbolIndicators(
        symbol=symbol,
        price_usdt=price,
        rsi_14=rsi_14,
        ema_fast=ema_fast,
        ema_slow=ema_slow,
        trend=trend,
    )
# ==== BLOCK: INDICATORS_BUILD - END ====
