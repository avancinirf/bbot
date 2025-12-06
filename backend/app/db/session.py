from sqlmodel import SQLModel, create_engine, Session

from app.core.config import get_settings
from . import models  # noqa: F401  # importa modelos para registrar metadados


settings = get_settings()

# Engine do SQLite (arquivo em ./data dentro do container)
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {},
)


def init_db() -> None:
    """Cria as tabelas se ainda não existirem."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Dependência para usar sessões de DB nas rotas."""
    with Session(engine) as session:
        yield session
