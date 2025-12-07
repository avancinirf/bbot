from __future__ import annotations

from sqlmodel import Session, create_engine

from app.core.config import get_settings

settings = get_settings()

connect_args = {}
if settings.database_url.startswith("sqlite"):
    # Necessário para SQLite + múltiplas threads (FastAPI)
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    echo=False,  # pode trocar pra True pra debugar SQL
    connect_args=connect_args,
)


def get_session() -> Session:
    """Dependência do FastAPI para injetar sessão de banco."""
    with Session(engine) as session:
        yield session
