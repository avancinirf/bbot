# ==== BLOCK: DB_IMPORTS - START ====
from sqlmodel import SQLModel, create_engine, Session
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
    from .models import Bot, BotAsset, TradeLog  # noqa: F401

    SQLModel.metadata.create_all(engine)
# ==== BLOCK: DB_INIT - END ====

