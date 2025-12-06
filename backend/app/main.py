from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import system as system_router
from app.api import bots as bots_router
from app.api import market as market_router
from app.db.session import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="Binance Microtrade Bot")

    # CORS liberado para o frontend React em dev
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inicializa o banco ao subir
    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    # Rotas da API
    app.include_router(system_router.router, prefix="/api")
    app.include_router(bots_router.router, prefix="/api")
    app.include_router(market_router.router, prefix="/api")

    @app.get("/health")
    def health_check() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
