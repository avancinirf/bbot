from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TradeBase(SQLModel):
    bot_id: int = Field(foreign_key="bot.id", index=True)
    symbol: str = Field(description="Par negociado, ex: BTCUSDT")
    side: str = Field(description="BUY ou SELL")
    price: float = Field(description="Preço unitário da moeda")
    qty: float = Field(description="Quantidade de moeda")
    quote_qty: float = Field(description="Valor em USDT gasto/recebido no trade")
    is_simulated: bool = Field(
        default=True,
        description="True = trade simulado; False = trade real (quando implementarmos)",
    )
    fee_amount: Optional[float] = Field(
        default=None,
        description="Valor da taxa cobrada, se disponível",
    )
    fee_asset: Optional[str] = Field(
        default=None,
        description="Moeda em que a taxa foi cobrada, se disponível",
    )
    realized_pnl: Optional[float] = Field(
        default=None,
        description="Lucro/Prejuízo realizado (apenas para SELL)",
    )
    info: Optional[str] = Field(
        default=None,
        description="Informações adicionais (texto livre)",
    )


class Trade(TradeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Momento da execução do trade (UTC)",
    )


class TradeRead(TradeBase):
    id: int
    created_at: datetime
