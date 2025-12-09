from __future__ import annotations

import hashlib
import hmac
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx

from app.core.config import get_settings

settings = get_settings()


def _get_base_url() -> str:
    """Testnet ou mainnet da Binance Spot."""
    if settings.binance_testnet:
        return "https://testnet.binance.vision"
    return "https://api.binance.com"


BASE_URL = _get_base_url()


def get_exchange_info(symbol: Optional[str] = None) -> dict:
    """Chama /api/v3/exchangeInfo na Binance.

    Se 'symbol' for passado, retorna info daquele par.
    """
    params: Dict[str, Any] = {}
    if symbol:
        params["symbol"] = symbol.upper()

    resp = httpx.get(
        f"{BASE_URL}/api/v3/exchangeInfo",
        params=params,
        timeout=10.0,
    )
    resp.raise_for_status()
    return resp.json()


def get_symbol_price(symbol: str) -> float:
    """Busca o último preço de um símbolo na Binance Spot.

    Usa um timeout configurável (se existir em settings) ou 10s por padrão.
    """
    url = f"{BASE_URL}/api/v3/ticker/price"
    params = {"symbol": symbol.upper()}

    timeout = getattr(settings, "binance_http_timeout", 10.0)
    with httpx.Client(timeout=timeout) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    return float(data["price"])


def validate_symbol(symbol: str) -> bool:
    """Retorna True se o símbolo existir na Binance, False caso contrário."""
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


def get_klines(
    symbol: str,
    interval: str = "5m",
    limit: int = 200,
) -> list[dict]:
    """Busca candles (klines) da Binance Spot."""
    url = f"{BASE_URL}/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}

    timeout = getattr(settings, "binance_http_timeout", 10.0)
    with httpx.Client(timeout=timeout) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    klines: list[dict] = []
    for row in data:
        open_time_ms = row[0]
        close_time_ms = row[6]

        open_time = datetime.fromtimestamp(
            open_time_ms / 1000.0, tz=timezone.utc
        ).replace(tzinfo=None)
        close_time = datetime.fromtimestamp(
            close_time_ms / 1000.0, tz=timezone.utc
        ).replace(tzinfo=None)

        kline = {
            "open_time": open_time,
            "close_time": close_time,
            "open": float(row[1]),
            "high": float(row[2]),
            "low": float(row[3]),
            "close": float(row[4]),
            "volume": float(row[5]),
        }
        klines.append(kline)

    return klines


def _signed_request(
    method: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
) -> dict:
    """Faz uma requisição assinada à Binance (endpoints privados)."""
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

    resp = httpx.request(
        method,
        url,
        params=params,
        headers=headers,
        timeout=10.0,
    )
    resp.raise_for_status()
    return resp.json()


def get_account_summary() -> dict:
    """Retorna um resumo simples da conta: canTrade + saldos > 0."""
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


def place_test_order(
    *,
    symbol: str,
    side: str,
    type_: str,
    quantity: Optional[float] = None,
    quote_order_qty: Optional[float] = None,
    time_in_force: Optional[str] = None,
    price: Optional[float] = None,
    extra_params: Optional[Dict[str, Any]] = None,
) -> dict:
    """Envia um /api/v3/order/test (não executa ordem real)."""
    params: Dict[str, Any] = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": type_.upper(),
    }

    if quantity is not None:
        params["quantity"] = quantity

    if quote_order_qty is not None:
        params["quoteOrderQty"] = quote_order_qty

    if time_in_force is not None:
        params["timeInForce"] = time_in_force

    if price is not None:
        params["price"] = price

    if extra_params:
        params.update(extra_params)

    # /order/test retorna {} em caso de sucesso
    return _signed_request("POST", "/api/v3/order/test", params=params)


def place_order(
    *,
    symbol: str,
    side: str,
    type_: str,
    quantity: Optional[float] = None,
    quote_order_qty: Optional[float] = None,
    time_in_force: Optional[str] = None,
    price: Optional[float] = None,
    extra_params: Optional[Dict[str, Any]] = None,
) -> dict:
    """Envia uma ordem real (/api/v3/order).

    - Se estiver em testnet (binance_testnet = True), a ordem é enviada para o ambiente de teste.
    - Se estiver em mainnet, é uma ordem real na sua conta.
    """
    params: Dict[str, Any] = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": type_.upper(),
    }

    if quantity is not None:
        params["quantity"] = quantity

    if quote_order_qty is not None:
        params["quoteOrderQty"] = quote_order_qty

    if time_in_force is not None:
        params["timeInForce"] = time_in_force

    if price is not None:
        params["price"] = price

    if extra_params:
        params.update(extra_params)

    return _signed_request("POST", "/api/v3/order", params=params)
