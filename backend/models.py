# ============================================================
# backend/models.py  —  ARQUIVO COMPLETO
# ============================================================

from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


# ============================================================
# BOT MODEL
# ============================================================

class BotBase(SQLModel):
    name: str
    initial_balance_usdt: float = 0.0
    current_balance_usdt: float = 0.0
    stop_loss_percent: float = 40.0
    stop_behavior: str = "STOP_ONLY"
    is_active: bool = False

    # Controle de rebalanceamento
    last_rebalance_at: Optional[datetime] = None
    last_rebalance_insufficient: bool = False

    # MODO DE TRADE (REAL ou SIMULATED)
    trade_mode: str = "SIMULATED"


class Bot(BotBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    assets: list["BotAsset"] = Relationship(back_populates="bot")
    logs: list["BotLog"] = Relationship(back_populates="bot")


class BotCreate(SQLModel):
    name: str
    initial_balance_usdt: float
    current_balance_usdt: float


class BotUpdate(SQLModel):
    name: Optional[str] = None
    initial_balance_usdt: Optional[float] = None
    current_balance_usdt: Optional[float] = None
    stop_loss_percent: Optional[float] = None
    stop_behavior: Optional[str] = None


class BotTradeModeUpdate(SQLModel):
    trade_mode: str


# ============================================================
# ASSET MODEL
# ============================================================

class BotAssetBase(SQLModel):
    symbol: str
    buy_percent: float
    sell_percent: float
    can_buy: bool = True
    can_sell: bool = True
    initial_price_usdt: float = 0.0
    reserved_amount: float = 0.0
    # Evita execução simultânea de trades no mesmo par
    is_locked: bool = False


class BotAsset(BotAssetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bot_id: int = Field(foreign_key="bot.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    bot: Optional[Bot] = Relationship(back_populates="assets")


# ============================================================
# CORREÇÃO IMPORTANTE
# (Agora buy_percent e sell_percent são opcionais)
# ============================================================

class BotAssetCreate(SQLModel):
    symbol: str
    buy_percent: Optional[float] = None
    sell_percent: Optional[float] = None


class BotAssetUpdate(SQLModel):
    buy_percent: Optional[float] = None
    sell_percent: Optional[float] = None
    can_buy: Optional[bool] = None
    can_sell: Optional[bool] = None


# ============================================================
# LOG MODEL
# ============================================================

class BotLogBase(SQLModel):
    bot_id: int
    side: str
    from_symbol: str
    to_symbol: str
    amount_from: float
    amount_to: float
    price_usdt: float
    message: str


class BotLog(BotLogBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    bot: Optional[Bot] = Relationship(back_populates="logs")
