# ==== BLOCK: IMPORTS - START ====
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import asyncio

from .db import init_db
from . import routes_bots
from . import routes_bot_assets
from . import routes_trade_logs
from . import routes_bot_analysis
from . import routes_bot_trade
from . import routes_bot_simtrade
from . import routes_bot_rebalance
from .bot_engine import start_bot_engine
from . import routes_bot_indicators
# ==== BLOCK: IMPORTS - END ====




# ==== BLOCK: APP_INSTANCE - START ====
app = FastAPI(title="Binance Micro Trade Bot - Backend")
# ==== BLOCK: APP_INSTANCE - END ====


# ==== BLOCK: CORS_MIDDLEWARE - START ====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois podemos limitar
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ==== BLOCK: CORS_MIDDLEWARE - END ====


# ==== BLOCK: API_ROUTER_BASE - START ====
api_router = APIRouter(prefix="/api")


@api_router.get("/health")
def health_check():
    """
    Endpoint simples para verificar se o backend está rodando.
    """
    return {"status": "ok", "service": "binance-trade-backend"}
# ==== BLOCK: API_ROUTER_BASE - END ====


# ==== BLOCK: INCLUDE_ROUTES_ASSETS - START ====
from . import routes_bot_assets
app.include_router(routes_bot_assets.router)
# ==== BLOCK: INCLUDE_ROUTES_ASSETS - END ====


# ==== BLOCK: INCLUDE_ROUTERS - START ====
# Rotas específicas
app.include_router(routes_bots.router)
app.include_router(routes_bot_assets.router)
app.include_router(routes_trade_logs.router)
app.include_router(routes_bot_analysis.router)
app.include_router(routes_bot_trade.router)
app.include_router(routes_bot_simtrade.router)
app.include_router(routes_bot_rebalance.router)
app.include_router(routes_bot_indicators.router)
# Rotas base (/api/health etc.)
app.include_router(api_router)
# ==== BLOCK: INCLUDE_ROUTERS - END ====




# ==== BLOCK: LIFESPAN_EVENTS - START ====
@app.on_event("startup")
def on_startup():
    """
    Executado quando a aplicação inicia.
    Garante que o banco e as tabelas foram criados.
    """
    init_db()
# ==== BLOCK: LIFESPAN_EVENTS - END ====


# ==== BLOCK: STARTUP_BOT_ENGINE - START ====
@app.on_event("startup")
async def startup_bot_engine():
    # Inicia o motor do bot em background
    asyncio.create_task(start_bot_engine())
# ==== BLOCK: STARTUP_BOT_ENGINE - END ====


# ==== BLOCK: STATIC_FILES_MOUNT - START ====
FRONTEND_DIST_DIR = os.getenv("FRONTEND_DIST_DIR", "/app/frontend/dist")

if os.path.isdir(FRONTEND_DIST_DIR):
    app.mount(
        "/",
        StaticFiles(directory=FRONTEND_DIST_DIR, html=True),
        name="frontend",
    )
# ==== BLOCK: STATIC_FILES_MOUNT - END ====
