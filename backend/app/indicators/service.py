from __future__ import annotations

from datetime import datetime
from typing import List

from sqlmodel import Session, select

from app.binance.client import get_klines
from app.db.session import engine
from app.models.indicator import Indicator


# ---------- helpers de indicadores simples ----------


def ema(values: list[float], period: int) -> list[float | None]:
    if not values:
        return []
    alpha = 2 / (period + 1)
    out: list[float | None] = []
    ema_prev: float | None = None
    for v in values:
        if ema_prev is None:
            ema_prev = v
        else:
            ema_prev = alpha * v + (1 - alpha) * ema_prev
        out.append(ema_prev)
    return out


def rsi(values: list[float], period: int = 14) -> list[float | None]:
    if len(values) < period + 1:
        return [None] * len(values)

    deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
    gains = [max(d, 0.0) for d in deltas]
    losses = [abs(min(d, 0.0)) for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    rsis: list[float | None] = [None] * (period)

    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            rs = float("inf")
        else:
            rs = avg_gain / avg_loss

        rsi_val = 100 - (100 / (1 + rs))
        rsis.append(rsi_val)

    rsis.append(rsis[-1])

    if len(rsis) < len(values):
        rsis = [None] * (len(values) - len(rsis)) + rsis
    return rsis[: len(values)]


def macd_series(values: list[float]) -> tuple[list[float | None], list[float | None], list[float | None]]:
    if not values:
        return [], [], []

    ema12 = ema(values, 12)
    ema26 = ema(values, 26)

    macd_line: list[float | None] = []
    for e12, e26 in zip(ema12, ema26):
        if e12 is None or e26 is None:
            macd_line.append(None)
        else:
            macd_line.append(e12 - e26)

    signal: list[float | None] = []
    ema_prev: float | None = None
    alpha = 2 / (9 + 1)
    for m in macd_line:
        if m is None:
            signal.append(None)
            continue
        if ema_prev is None:
            ema_prev = m
        else:
            ema_prev = alpha * m + (1 - alpha) * ema_prev
        signal.append(ema_prev)

    hist: list[float | None] = []
    for m, s in zip(macd_line, signal):
        if m is None or s is None:
            hist.append(None)
        else:
            hist.append(m - s)

    return macd_line, signal, hist


def compute_trend_and_signals(
    ema9: float | None,
    ema21: float | None,
    macd_val: float | None,
    macd_signal_val: float | None,
    adx: float | None,
    rsi14: float | None,
) -> tuple[float | None, str | None, bool | None, bool | None]:
    """
    Implementa exatamente as regras descritas no documento:
    - trend_score
    - trend_label
    - market_signal_compra
    - market_signal_venda
    """
    if ema9 is None or ema21 is None or macd_val is None or macd_signal_val is None:
        return None, None, None, None

    score = 0.0

    if ema9 > ema21:
        score += 1
    else:
        score -= 1

    if macd_val > macd_signal_val:
        score += 1
    else:
        score -= 1

    if adx is not None:
        if adx > 25:
            score *= 1.5
        elif adx < 20:
            score *= 0.5

    if score >= 1:
        label = "bullish"
    elif score <= -1:
        label = "bearish"
    else:
        label = "neutral"

    market_buy: bool | None = None
    market_sell: bool | None = None

    if rsi14 is None:
        return score, label, None, None

    if label == "bullish":
        market_buy = True
        market_sell = False
    elif label == "bearish":
        market_buy = False
        market_sell = True
    else:
        if 40 <= rsi14 <= 60:
            market_buy = True
            market_sell = True
        else:
            market_buy = False
            market_sell = False

    return score, label, market_buy, market_sell


# ---------- serviço principal de sync ----------


def sync_indicators_for_symbol(
    symbol: str,
    interval: str = "5m",
    limit: int = 200,
) -> int:
    """
    Busca candles na Binance, calcula indicadores e grava na tabela indicator.

    Retorna quantas linhas NOVAS foram inseridas.
    """
    klines = get_klines(symbol=symbol, interval=interval, limit=limit)
    if not klines:
        return 0

    closes = [k["close"] for k in klines]

    ema9_series = ema(closes, 9)
    ema21_series = ema(closes, 21)
    rsi_series = rsi(closes, 14)
    macd_line, macd_signal, macd_hist = macd_series(closes)

    with Session(engine) as session:
        last = session.exec(
            select(Indicator)
            .where(Indicator.symbol == symbol, Indicator.interval == interval)
            .order_by(Indicator.open_time.desc())
        ).first()

        last_open_time: datetime | None = last.open_time if last else None

        inserted = 0
        for idx, k in enumerate(klines):
            open_time = k["open_time"]

            if last_open_time and open_time <= last_open_time:
                continue

            close_time = k["close_time"]
            close = k["close"]

            ema9_val = ema9_series[idx]
            ema21_val = ema21_series[idx]
            rsi_val = rsi_series[idx]
            macd_val = macd_line[idx]
            macd_sig_val = macd_signal[idx]
            macd_hist_val = macd_hist[idx]

            adx_val = None  # ADX fica para uma próxima etapa, se quiser

            trend_score, trend_label, m_buy, m_sell = compute_trend_and_signals(
                ema9_val,
                ema21_val,
                macd_val,
                macd_sig_val,
                adx_val,
                rsi_val,
            )

            ind = Indicator(
                symbol=symbol,
                interval=interval,
                open_time=open_time,
                close_time=close_time,
                close=close,
                ema9=ema9_val,
                ema21=ema21_val,
                rsi14=rsi_val,
                macd=macd_val,
                macd_signal=macd_sig_val,
                macd_hist=macd_hist_val,
                adx=adx_val,
                trend_score=trend_score,
                trend_label=trend_label,
                market_signal_compra=m_buy,
                market_signal_venda=m_sell,
            )

            session.add(ind)
            inserted += 1

        if inserted > 0:
            session.commit()

        return inserted
