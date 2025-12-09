from __future__ import annotations

import sys
import traceback

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from app.db.session import engine
from app.indicators.service import sync_indicators_for_symbol
from app.models.indicator import Indicator

# IMPORTANTE: prefix volta a ser /indicators, pois o frontend chama /indicators/latest/{symbol}
router = APIRouter(prefix="/indicators", tags=["indicators"])


@router.get("/ping")
def ping_indicators():
    return {"message": "indicators endpoint ok"}


@router.post("/sync/{symbol}")
def sync_symbol_indicators(symbol: str):
    """
    Sincroniza indicadores para um símbolo (ex: BTCUSDT).
    Em caso de erro, devolve o texto da exceção em `detail`
    para facilitar o debug via curl.
    """
    symbol = symbol.upper()

    try:
        inserted = sync_indicators_for_symbol(symbol, interval="5m", limit=200)
        return {"symbol": symbol, "inserted": inserted}
    except Exception as e:
        # Loga stack trace no console do container
        print("[INDICATORS] Erro ao sincronizar indicadores:", repr(e), file=sys.stderr)
        traceback.print_exc()

        # Devolve mensagem de erro para o cliente
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest/{symbol}")
def get_latest_indicator(symbol: str):
    symbol = symbol.upper()

    with Session(engine) as session:
        ind = (
            session.exec(
                select(Indicator)
                .where(
                    Indicator.symbol == symbol,
                    Indicator.interval == "5m",
                )
                .order_by(Indicator.close_time.desc())
            )
            .first()
        )

        if not ind:
            raise HTTPException(
                status_code=404,
                detail="Nenhum indicador encontrado para esse símbolo.",
            )

        return ind
