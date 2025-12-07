from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx

from app.core.config import get_settings

settings = get_settings()


def _get_base_url() -> str:
    # Testnet ou mainnet da Binance Spot
    if settings.binance_testnet:
        return "https://testnet.binance.vision"
    return "https://api.binance.com"


BASE_URL = _get_base_url()


def get_exchange_info(symbol: Optional[str] = None) -> dict:
    """
    Chama /api/v3/exchangeInfo na Binance.
    Se 'symbol' for passado, retorna info daquele par.
    """
    params: Dict[str, Any] = {}
    if symbol:
        params["symbol"] = symbol.upper()

    resp = httpx.get(f"{BASE_URL}/api/v3/exchangeInfo", params=params, timeout=10.0)
    resp.raise_for_status()
    return resp.json()


def get_symbol_price(symbol: str) -> float:
    """
    Retorna o preço atual do símbolo (ticker price) na Binance.
    """
    symbol = symbol.upper().strip()
    if not symbol:
        raise ValueError("Símbolo vazio inválido.")

    resp = httpx.get(
        f"{BASE_URL}/api/v3/ticker/price",
        params={"symbol": symbol},
        timeout=10.0,
    )
    resp.raise_for_status()
    data = resp.json()
    return float(data["price"])


def validate_symbol(symbol: str) -> bool:
    """
    Retorna True se o símbolo existir na Binance, False caso contrário.
    Não levanta erro para símbolo inválido, apenas False.
    """
    symbol = symbol.upper().strip()
    if not symbol:
        return False

    try:
        data = get_exchange_info(symbol)
    except httpx.HTTPStatusError:
        return False
    except httpx.HTTPError:
        return False

    syms = data.get("symbols", [])
    return any(s.get("symbol") == symbol for s in syms)


def _signed_request(method: str, path: str, params: Optional[Dict[str, Any]] = None) -> dict:
    """
    Faz uma requisição assinada à Binance (para endpoints privados, ex: /api/v3/account).
    """
    if not settings.binance_api_key or not settings.binance_api_secret:
        raise RuntimeError("Chaves da Binance não configuradas.")

    if params is None:
        params = {}

    params.setdefault("timestamp", int(time.time() * 1000))
    params.setdefault("recvWindow", 5000)

    query_str = urlencode(params, doseq=True)
    signature = hmac.new(
        settings.binance_api_secret.encode("utf-8"),
        query_str.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    params["signature"] = signature

    headers = {"X-MBX-APIKEY": settings.binance_api_key}

    url = f"{BASE_URL}{path}"
    resp = httpx.request(method, url, params=params, headers=headers, timeout=10.0)
    resp.raise_for_status()
    return resp.json()


def get_account_summary() -> dict:
    """
    Retorna um resumo simples da conta:
    - canTrade
    - lista de balances com saldos > 0.
    """
    data = _signed_request("GET", "/api/v3/account")

    balances_raw = data.get("balances", [])
    balances = []
    for b in balances_raw:
        free = float(b.get("free", "0"))
        locked = float(b.get("locked", "0"))
        if free > 0 or locked > 0:
            balances.append(
                {
                    "asset": b["asset"],
                    "free": free,
                    "locked": locked,
                }
            )

    return {
        "canTrade": data.get("canTrade", False),
        "balances": balances,
    }
