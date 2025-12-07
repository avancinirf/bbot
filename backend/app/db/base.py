from __future__ import annotations

from sqlmodel import SQLModel

from app.db.session import engine
from app import models  # importa modelos para registrar no metadata


def init_db() -> None:
    """Cria as tabelas no banco, caso não existam."""
    SQLModel.metadata.create_all(bind=engine)
