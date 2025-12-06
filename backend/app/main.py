from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import system as system_router
from app.api import bots as bots_router
from app.api import market as market_router
from app.db.session import init_db

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path


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


# --------------------------------------------------------------------
# Servir frontend React (build Vite) a partir do mesmo container
# --------------------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent.parent  # /app/backend
FRONTEND_DIST_DIR = BACKEND_DIR.parent / "frontend_dist"  # /app/frontend_dist

if FRONTEND_DIST_DIR.exists():
    # Rota raiz "/" devolve o index.html do Vite
    @app.get("/", response_class=HTMLResponse)
    async def serve_frontend_root() -> str:
        index_file = FRONTEND_DIST_DIR / "index.html"
        return index_file.read_text(encoding="utf-8")

    # Arquivos estáticos (/assets/...) gerados pelo Vite
    assets_dir = FRONTEND_DIST_DIR / "assets"
    if assets_dir.exists():
        app.mount(
            "/assets",
            StaticFiles(directory=assets_dir),
            name="frontend-assets",
        )
