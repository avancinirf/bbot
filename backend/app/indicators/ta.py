from __future__ import annotations

import numpy as np
import pandas as pd


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)

    roll_up = up.ewm(alpha=1 / period, adjust=False).mean()
    roll_down = down.ewm(alpha=1 / period, adjust=False).mean()

    rs = roll_up / roll_down
    rsi_val = 100 - (100 / (1 + rs))
    return rsi_val


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def adx(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    prev_close = close.shift(1)

    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm = np.where((plus_dm > 0) & (plus_dm > minus_dm), plus_dm, 0.0)
    minus_dm = np.where((minus_dm > 0) & (minus_dm > plus_dm), minus_dm, 0.0)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.ewm(alpha=1 / period, adjust=False).mean()

    plus_di = 100 * pd.Series(plus_dm, index=high.index).ewm(
        alpha=1 / period, adjust=False
    ).mean() / atr
    minus_di = 100 * pd.Series(minus_dm, index=low.index).ewm(
        alpha=1 / period, adjust=False
    ).mean() / atr

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).abs()
    adx_val = dx.ewm(alpha=1 / period, adjust=False).mean()
    return adx_val


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recebe DataFrame com colunas:
      - open_time, open, high, low, close, volume
    Retorna DataFrame com colunas de indicadores adicionadas.
    """
    df = df.sort_values("open_time").reset_index(drop=True).copy()

    close = df["close"]
    high = df["high"]
    low = df["low"]

    df["ema9"] = ema(close, 9)
    df["ema21"] = ema(close, 21)
    df["rsi14"] = rsi(close, 14)

    macd_line, signal_line, hist = macd(close, 12, 26, 9)
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["macd_hist"] = hist

    df["adx"] = adx(high, low, close, 14)

    # Índice de tendência simplificado
    score = np.zeros(len(df))

    # EMA9 vs EMA21
    score += np.where(df["ema9"] > df["ema21"], 1, -1)

    # MACD vs signal
    score += np.where(df["macd"] > df["macd_signal"], 1, -1)

    # Ajuste pela força da tendência (ADX)
    score = np.where(df["adx"] > 25, score * 1.5, score)
    score = np.where(df["adx"] < 20, score * 0.5, score)

    df["trend_score"] = score

    # Labels
    labels = np.array(["neutral"] * len(df), dtype=object)
    labels = np.where(df["trend_score"] >= 1, "bullish", labels)
    labels = np.where(df["trend_score"] <= -1, "bearish", labels)
    df["trend_label"] = labels

    # Sinais de mercado para compra/venda
    df["market_signal_compra"] = False
    df["market_signal_venda"] = False

    neutral_rsi = df["rsi14"].between(40, 60)

    df.loc[df["trend_label"] == "bullish", "market_signal_compra"] = True
    df.loc[df["trend_label"] == "neutral", "market_signal_compra"] = neutral_rsi

    df.loc[df["trend_label"] == "bearish", "market_signal_venda"] = True
    df.loc[df["trend_label"] == "neutral", "market_signal_venda"] = neutral_rsi

    return df
