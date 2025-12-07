from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Indicator(SQLModel, table=True):
    """
    Tabela de indicadores por símbolo/candle.

    Intervalo inicial: sempre '5m'.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    symbol: str = Field(index=True, description="Símbolo da Binance, ex: BTCUSDT")
    interval: str = Field(
        default="5m",
        description="Intervalo do candle, ex: 5m",
        index=True,
    )

    # Tempo de abertura/fechamento do candle
    open_time: datetime = Field(index=True)
    close_time: datetime = Field(index=True)

    # Preço de fechamento
    close: float

    # Indicadores básicos
    ema9: Optional[float] = None
    ema21: Optional[float] = None
    rsi14: Optional[float] = None

    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None

    adx: Optional[float] = None

    # Índice de tendência
    trend_score: Optional[float] = None
    trend_label: Optional[str] = Field(
        default=None,
        description="bullish / bearish / neutral",
        index=True,
    )

    # Sinais de mercado
    market_signal_compra: Optional[bool] = Field(default=None, index=True)
    market_signal_venda: Optional[bool] = Field(default=None, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
