# ==== BLOCK: DB_IMPORTS - START ====
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
from pathlib import Path
# ==== BLOCK: DB_IMPORTS - END ====


# ==== BLOCK: DB_CONFIG - START ====
# Caminho do arquivo SQLite.
DB_PATH = Path("./data/bot.db")
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DB_URL,
    echo=False,  # pode mudar para True se quiser ver os SQLs no log
    connect_args={"check_same_thread": False},
)
# ==== BLOCK: DB_CONFIG - END ====


# ==== BLOCK: DB_SESSION_HELPER - START ====
def get_session() -> Session:
    """
    Helper para obter uma Session do SQLModel.
    """
    return Session(engine)
# ==== BLOCK: DB_SESSION_HELPER - END ====


# ==== BLOCK: DB_INIT - START ====
def init_db():
    """
    Cria o arquivo e as tabelas do banco, se ainda não existirem.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Import local para registrar os modelos antes do create_all
    from .models import Bot, BotAsset, BotLog  # noqa: F401

    SQLModel.metadata.create_all(engine)
    apply_migrations()
# ==== BLOCK: DB_INIT - END ====

def _column_exists(conn, table: str, column: str) -> bool:
    result = conn.execute(text(f"PRAGMA table_info({table});"))
    return column in {row[1] for row in result}


def _add_column_if_missing(conn, table: str, column: str, definition: str) -> None:
    if not _column_exists(conn, table, column):
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {definition}"))


def apply_migrations() -> None:
    """
    Pequenas migrações manuais para alinhar tabelas existentes
    com os modelos atuais. Importante para quem já tinha um
    bot.db criado antes das últimas alterações de schema.
    """

    with engine.begin() as conn:
        # BOT
        _add_column_if_missing(conn, "bot", "trade_mode", "TEXT NOT NULL DEFAULT 'SIMULATED'")
        _add_column_if_missing(conn, "bot", "last_rebalance_at", "DATETIME")
        _add_column_if_missing(conn, "bot", "last_rebalance_insufficient", "BOOLEAN NOT NULL DEFAULT 0")
        _add_column_if_missing(conn, "bot", "created_at", "DATETIME")
        _add_column_if_missing(conn, "bot", "updated_at", "DATETIME")

        # BOT ASSET
        _add_column_if_missing(conn, "botasset", "initial_price_usdt", "REAL NOT NULL DEFAULT 0")
        _add_column_if_missing(conn, "botasset", "reserved_amount", "REAL NOT NULL DEFAULT 0")
        _add_column_if_missing(conn, "botasset", "can_buy", "BOOLEAN NOT NULL DEFAULT 1")
        _add_column_if_missing(conn, "botasset", "can_sell", "BOOLEAN NOT NULL DEFAULT 1")
        _add_column_if_missing(conn, "botasset", "created_at", "DATETIME")
        _add_column_if_missing(conn, "botasset", "updated_at", "DATETIME")
        _add_column_if_missing(conn, "botasset", "is_locked", "BOOLEAN NOT NULL DEFAULT 0")

        # BOT LOG
        _add_column_if_missing(conn, "botlog", "created_at", "DATETIME")
