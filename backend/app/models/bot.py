from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class BotBase(SQLModel):
    name: str = Field(description="Nome amigável do bot")
    symbol: str = Field(description="Par negociado, ex: BTCUSDT")

    saldo_usdt_limit: float = Field(description="Limite máximo de USDT (saldo virtual do bot)")
    stop_loss_percent: float = Field(
        default=0.0,
        description="Stop loss em %, ex: 20 = -20%",
    )
    vender_stop_loss: bool = Field(
        default=True,
        description="Se true, vende tudo quando o stop loss disparar",
    )

    # Estratégia de compra/venda por percentual
    porcentagem_compra: float = Field(
        default=0.0,
        description="0 desativa; >0 = só compra se preço atual estiver X% abaixo de valor_inicial",
    )
    porcentagem_venda: float = Field(
        default=0.0,
        description="0 desativa; >0 = só vende se preço atual estiver X% acima de valor_inicial",
    )

    # Flags
    comprar_ao_iniciar: bool = Field(
        default=False,
        description="Se true, faz a primeira compra automaticamente ao iniciar o bot",
    )
    compra_mercado: bool = Field(
        default=True,
        description="Se true, respeita sinal de mercado para compra (futuro uso com indicadores)",
    )
    venda_mercado: bool = Field(
        default=True,
        description="Se true, respeita sinal de mercado para venda (futuro uso com indicadores)",
    )

    valor_de_trade_usdt: float = Field(
        description="Valor de cada trade em USDT, ex: 10",
    )


class Bot(BotBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    status: str = Field(
        default="offline",
        description="online/offline",
        index=True,
    )
    blocked: bool = Field(
        default=False,
        description="Quando true, não pode ficar online",
        index=True,
    )

    saldo_usdt_livre: float = Field(
        default=0.0,
        description="Saldo virtual livre atual do bot em USDT",
    )

    # Estado da posição
    has_open_position: bool = Field(default=False)
    qty_moeda: float = Field(default=0.0)
    last_buy_price: Optional[float] = None
    last_sell_price: Optional[float] = None
    valor_inicial: Optional[float] = Field(
        default=None,
        description="Preço de referência do ciclo atual (compra/venda)",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Quando o bot foi criado",
    )
    started_at: Optional[datetime] = Field(
        default=None,
        description="Quando foi iniciado pela primeira vez",
    )


class BotCreate(BotBase):
    """
    Modelo usado para criação de bot via API.
    """


class BotRead(BotBase):
    """
    Modelo retornado para o frontend.
    """
    id: int
    status: str
    blocked: bool
    saldo_usdt_livre: float

    has_open_position: bool
    qty_moeda: float
    last_buy_price: Optional[float]
    last_sell_price: Optional[float]
    valor_inicial: Optional[float]
    created_at: datetime
    started_at: Optional[datetime]
