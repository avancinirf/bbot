from __future__ import annotations

from typing import Literal, Optional

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.binance.client import (
    get_account_summary,
    validate_symbol as binance_validate_symbol,
    place_test_order as binance_place_test_order,
    place_order as binance_place_order,
)
from app.core.config import get_settings

router = APIRouter(prefix="/binance", tags=["binance"])


class OrderTestRequest(BaseModel):
    symbol: str = Field(..., description="Par de negociação, ex: BTCUSDT")
    side: Literal["BUY", "SELL"]
    type: Literal["MARKET", "LIMIT"] = "MARKET"

    # OU quantity (moeda base) OU quoteOrderQty (USDT)
    quantity: Optional[float] = Field(
      None,
      gt=0,
      description="Quantidade da moeda base (ex: BTC)",
    )
    quoteOrderQty: Optional[float] = Field(
      None,
      gt=0,
      description="Quantidade em USDT (ou moeda de cotação) para ordens MARKET",
    )

    price: Optional[float] = Field(
      None,
      gt=0,
      description="Preço para ordens LIMIT",
    )
    timeInForce: Optional[str] = Field(
      default=None,
      description="GTC, IOC, FOK. Para LIMIT, default = GTC.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "MARKET",
                "quoteOrderQty": 10.0,
            }
        }


@router.get("/symbol/{symbol}/validate")
def validate_symbol_route(symbol: str) -> dict:
    """Valida se o símbolo existe na Binance."""
    ok = binance_validate_symbol(symbol)
    return {"symbol": symbol.upper(), "valid": ok}


@router.get("/account/summary")
def account_summary() -> dict:
    """Retorna um resumo simples da conta Binance.

    Se não houver chaves configuradas, retorna connected = False.
    """
    settings = get_settings()
    if not settings.binance_api_key or not settings.binance_api_secret:
        return {
            "mode": settings.app_mode,
            "testnet": settings.binance_testnet,
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
        "testnet": settings.binance_testnet,
        "connected": True,
        "balances": summary["balances"],
        "canTrade": summary["canTrade"],
    }


@router.post("/order/test")
def test_order(payload: OrderTestRequest) -> dict:
    """Testa uma ordem na Binance usando /api/v3/order/test.

    NÃO executa trade de verdade, apenas valida parâmetros e saldo.
    """
    settings = get_settings()

    # Confere se temos chaves
    if not settings.binance_api_key or not settings.binance_api_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chaves da Binance não configuradas.",
        )

    symbol = payload.symbol.upper()
    side = payload.side.upper()
    order_type = payload.type.upper()

    # Regras mínimas
    if payload.quantity is None and payload.quoteOrderQty is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe 'quantity' ou 'quoteOrderQty'.",
        )

    if payload.quantity is not None and payload.quoteOrderQty is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use apenas 'quantity' OU 'quoteOrderQty', não ambos.",
        )

    if order_type == "LIMIT" and payload.price is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Para ordens LIMIT é obrigatório informar 'price'.",
        )

    time_in_force = payload.timeInForce or ("GTC" if order_type == "LIMIT" else None)

    try:
        binance_result = binance_place_test_order(
            symbol=symbol,
            side=side,
            type_=order_type,
            quantity=payload.quantity,
            quote_order_qty=payload.quoteOrderQty,
            price=payload.price,
            time_in_force=time_in_force,
        )
    except RuntimeError as e:
        # Erros de configuração/proteção
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except httpx.HTTPStatusError as e:
        # Erro retornado pela própria Binance (saldo, parâmetros, etc)
        detail_msg = e.response.text
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro da Binance: {detail_msg}",
        )
    except httpx.HTTPError as e:
        # Erro de rede/conexão
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao comunicar com a Binance: {e}",
        )

    return {
        "mode": settings.app_mode,
        "testnet": settings.binance_testnet,
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": payload.quantity,
        "quoteOrderQty": payload.quoteOrderQty,
        "price": payload.price,
        "timeInForce": time_in_force,
        "binance_response": binance_result,  # normalmente {}
    }


@router.post("/order/place")
def place_order_route(payload: OrderTestRequest) -> dict:
    """Envia uma ordem real para a Binance (/api/v3/order).

    - Em testnet (binance_testnet = True): executa na conta de teste.
    - Em mainnet:
        - só permite se app_mode == "real" (proteção extra).
    """
    settings = get_settings()

    if not settings.binance_api_key or not settings.binance_api_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chaves da Binance não configuradas.",
        )

    symbol = payload.symbol.upper()
    side = payload.side.upper()
    order_type = payload.type.upper()

    # Proteção extra para mainnet:
    if not settings.binance_testnet and settings.app_mode != "real":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Envio de ordens reais em mainnet só é permitido com APP_MODE=real. "
                "Ajuste o .env se quiser habilitar isso conscientemente."
            ),
        )

    if payload.quantity is None and payload.quoteOrderQty is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe 'quantity' ou 'quoteOrderQty'.",
        )

    if payload.quantity is not None and payload.quoteOrderQty is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use apenas 'quantity' OU 'quoteOrderQty', não ambos.",
        )

    if order_type == "LIMIT" and payload.price is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Para ordens LIMIT é obrigatório informar 'price'.",
        )

    time_in_force = payload.timeInForce or ("GTC" if order_type == "LIMIT" else None)

    try:
        binance_result = binance_place_order(
            symbol=symbol,
            side=side,
            type_=order_type,
            quantity=payload.quantity,
            quote_order_qty=payload.quoteOrderQty,
            price=payload.price,
            time_in_force=time_in_force,
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except httpx.HTTPStatusError as e:
        detail_msg = e.response.text
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro da Binance: {detail_msg}",
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao comunicar com a Binance: {e}",
        )

    return {
        "mode": settings.app_mode,
        "testnet": settings.binance_testnet,
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": payload.quantity,
        "quoteOrderQty": payload.quoteOrderQty,
        "price": payload.price,
        "timeInForce": time_in_force,
        "binance_response": binance_result,
    }
