from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


# --------------------------------------------------------------------
# Enums básicos
# --------------------------------------------------------------------


class BotStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BLOCKED = "blocked"


class TradeSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


# --------------------------------------------------------------------
# Estado global do sistema
# --------------------------------------------------------------------


class SystemState(SQLModel, table=True):
    """
    Estado global do sistema:
    - online: se o engine pode rodar bots
    - simulation_mode: se ordens são simuladas ou reais
    """
    id: int | None = Field(default=1, primary_key=True)
    online: bool = Field(default=False)
    simulation_mode: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# --------------------------------------------------------------------
# Bot
# --------------------------------------------------------------------


class Bot(SQLModel, table=True):
    """
    Bot básico (vamos expandir com lógica de engine).
    """
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    status: BotStatus = Field(default=BotStatus.OFFLINE)

    # Saldo virtual do bot (não usa toda a conta)
    saldo_usdt_limit: float = Field(default=0.0, ge=0)
    saldo_usdt_livre: float = Field(default=0.0, ge=0)

    # Stop loss global do bot, em %
    # ex.: -20 = -20% em relação ao valor inicial do bot
    stop_loss_percent: float = Field(default=-20.0)

    # Flags de comportamento
    comprar_ao_iniciar: bool = Field(default=False)
    compra_mercado: bool = Field(default=True)
    venda_mercado: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# --------------------------------------------------------------------
# Pares do bot (uma posição por par/moeda)
# --------------------------------------------------------------------


class BotPair(SQLModel, table=True):
    """
    Configuração de cada par (ex.: BTCUSDT) dentro de um bot.
    """
    id: int | None = Field(default=None, primary_key=True)

    bot_id: int = Field(foreign_key="bot.id", index=True)
    symbol: str = Field(index=True)  # ex.: BTCUSDT

    # Valor de trade por operação (em USDT)
    valor_de_trade_usdt: float = Field(default=10.0, gt=0)

    # Preço de referência:
    # - última compra/venda
    # - ou valor quando a moeda foi adicionada ao bot
    valor_inicial: float | None = Field(default=None, ge=0)

    # porcentagem_compra:
    #   0 = regra desativada
    #   negativo (ex.: -5) = só compra se preço cair >= 5% vs valor_inicial
    porcentagem_compra: float = Field(default=0.0)

    # porcentagem_venda:
    #   0 = regra desativada
    #   positivo (ex.: 5) = só vende se preço subir >= 5% vs valor_inicial
    porcentagem_venda: float = Field(default=0.0)

    # Posição atual da moeda neste bot
    has_open_position: bool = Field(default=False)
    qty_moeda: float = Field(default=0.0, ge=0)
    last_buy_price: float | None = Field(default=None, ge=0)
    last_sell_price: float | None = Field(default=None, ge=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# --------------------------------------------------------------------
# Trades executados (simulados ou reais)
# --------------------------------------------------------------------


class Trade(SQLModel, table=True):
    """
    Registro de todas as transações realizadas pelos bots.
    """
    id: int | None = Field(default=None, primary_key=True)

    bot_id: int = Field(foreign_key="bot.id", index=True)
    bot_pair_id: int = Field(foreign_key="botpair.id", index=True)
    symbol: str = Field(index=True)  # ex.: BTCUSDT

    side: TradeSide

    qty: float = Field(gt=0)       # quantidade da moeda
    price: float = Field(gt=0)     # preço executado
    value_usdt: float = Field(gt=0)  # qty * price
    fee_usdt: float = Field(default=0.0, ge=0)

    # P&L em USDT (para essa operação ou round-trip, vamos definir depois)
    pnl_usdt: float | None = Field(default=None)

    # Snapshots de contexto na hora da decisão
    # strings JSON para simplificar o schema
    indicator_snapshot: str | None = Field(
        default=None,
        description="JSON com indicadores usados (close, EMA, RSI, etc.).",
    )
    rule_snapshot: str | None = Field(
        default=None,
        description="Resumo da regra aplicada para comprar/vender.",
    )

    # Preenchido apenas quando for ordem real na Binance
    binance_order_id: str | None = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)


# --------------------------------------------------------------------
# Candles (5m)
# --------------------------------------------------------------------


class Candle(SQLModel, table=True):
    """
    Candles de 5m por símbolo.
    Retenção 'para sempre' (podemos podar depois, se quiser).
    """
    id: int | None = Field(default=None, primary_key=True)

    symbol: str = Field(index=True)
    open_time: datetime = Field(index=True)

    open: float
    high: float
    low: float
    close: float
    volume: float

    created_at: datetime = Field(default_factory=datetime.utcnow)


# --------------------------------------------------------------------
# Indicadores calculados por candle
# --------------------------------------------------------------------


class Indicator(SQLModel, table=True):
    """
    Indicadores de mercado calculados em cima dos candles de 5m.
    """
    id: int | None = Field(default=None, primary_key=True)

    symbol: str = Field(index=True)
    open_time: datetime = Field(index=True)

    # close do candle (por praticidade, fica aqui também)
    close: float

    # Indicadores básicos
    ema9: float | None = None
    ema21: float | None = None
    rsi14: float | None = None

    # MACD (12, 26, 9)
    macd: float | None = None
    macd_signal: float | None = None
    macd_hist: float | None = None

    # Força de tendência
    adx: float | None = None

    # Índice de tendência simplificado (score + label)
    trend_score: float | None = None
    trend_label: str | None = Field(default=None)  # bullish / bearish / neutral

    # Sinais já prontos para o bot usar nas regras
    market_signal_compra: bool | None = None
    market_signal_venda: bool | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
