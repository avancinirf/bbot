from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.base import init_db
from app.api.routes_bots import router as bots_router
from app.api.routes_system import router as system_router
from app.api.routes_binance import router as binance_router
from app.api.routes_indicators import router as indicators_router
from app.engine.runner import bot_engine_loop


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title=settings.app_name)

    # CORS liberado por enquanto (frontend React local e depois no mesmo container)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rotas
    app.include_router(system_router)
    app.include_router(bots_router)
    app.include_router(binance_router)
    app.include_router(indicators_router, prefix="/indicators", tags=["indicators"])

    @app.get("/")
    def read_root():
        return {"message": "bbot API up", "mode": settings.app_mode}

    @app.on_event("startup")
    async def on_startup():
        # Inicializa o banco
        init_db()
        # Inicia o loop do engine em background
        asyncio.create_task(bot_engine_loop())
        print("[STARTUP] API inicializada e engine de bots agendado.")

    return app


app = create_app()
