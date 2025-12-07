from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException, status

from app.binance.client import get_account_summary, validate_symbol as binance_validate_symbol
from app.core.config import get_settings

router = APIRouter(prefix="/binance", tags=["binance"])


@router.get("/symbol/{symbol}/validate")
def validate_symbol_route(symbol: str) -> dict:
    """
    Valida se o símbolo existe na Binance.
    Sempre responde 200, com valid = True/False.
    """
    ok = binance_validate_symbol(symbol)
    return {"symbol": symbol.upper(), "valid": ok}


@router.get("/account/summary")
def account_summary() -> dict:
    """
    Retorna um resumo simples da conta Binance.
    Se não houver chaves configuradas, retorna connected = False.
    """
    settings = get_settings()

    if not settings.binance_api_key or not settings.binance_api_secret:
        return {
            "mode": settings.app_mode,
            "connected": False,
            "reason": "Chaves da Binance não configuradas",
            "balances": [],
            "canTrade": False,
        }

    try:
        summary = get_account_summary()
    except RuntimeError as e:
        # Erro de configuração (chaves)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except httpx.HTTPError as e:
        # Erro de conexão com a Binance
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao comunicar com a Binance: {e}",
        )

    return {
        "mode": settings.app_mode,
        "connected": True,
        "balances": summary["balances"],
        "canTrade": summary["canTrade"],
    }
