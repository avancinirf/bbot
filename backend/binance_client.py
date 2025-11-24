# ============================================================
# backend/binance_client.py — VERSÃO COMPLETA E ATUALIZADA
# ============================================================

import os
import time
import hmac
import hashlib
import requests
import logging

# ------------------------------------------------------------
# CONFIGURAÇÕES
# ------------------------------------------------------------

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
USE_TESTNET = os.getenv("BINANCE_TESTNET", "false").lower() == "true"

if USE_TESTNET:
    BASE_URL = "https://testnet.binance.vision"
else:
    BASE_URL = "https://api.binance.com"

logger = logging.getLogger("binance_client")
logger.setLevel(logging.INFO)


# ------------------------------------------------------------
# CRIA CLIENTE HTTP
# ------------------------------------------------------------

session = requests.Session()
session.headers.update({"X-MBX-APIKEY": BINANCE_API_KEY})


# ------------------------------------------------------------
# ASSINAR REQUISIÇÕES PRIVADAS
# ------------------------------------------------------------

def sign_request(params: dict) -> dict:
    query = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(
        BINANCE_API_SECRET.encode(),
        query.encode(),
        hashlib.sha256
    ).hexdigest()
    return {**params, "signature": signature}


# ------------------------------------------------------------
# VALIDAR SE PAR EXISTE
# ------------------------------------------------------------

def validate_symbol_exists(symbol: str) -> bool:
    """
    Valida se uma SYMBOL existe na Binance.
    Faz isso tentando buscar o ticker de preço.
    """
    symbol = symbol.upper()
    pair = f"{symbol}USDT"

    try:
        url = f"{BASE_URL}/api/v3/ticker/price"
        r = session.get(url, params={"symbol": pair}, timeout=5)
        if r.status_code == 200:
            return True
    except Exception:
        pass

    return False


# ------------------------------------------------------------
# PREÇO USDT — MESMO SE O PAR FOR INVERTIDO
# ------------------------------------------------------------

def get_symbol_price_usdt(symbol: str) -> float:
    """
    Retorna o preço da moeda em USDT.
    Caso o par seja invertido (ex: USDTBTC), converte corretamente.
    """
    symbol = symbol.upper()

    # TENTA SYMBOLUSDT
    pair = f"{symbol}USDT"
    url = f"{BASE_URL}/api/v3/ticker/price"
    r = session.get(url, params={"symbol": pair})

    if r.status_code == 200:
        return float(r.json()["price"])

    # TENTA USDTsymbol (invertido)
    pair_inv = f"USDT{symbol}"
    r = session.get(url, params={"symbol": pair_inv})

    if r.status_code == 200:
        price = float(r.json()["price"])
        return 1 / price  # inverter

    raise Exception(f"Não foi possível buscar preço USDT para {symbol}")


# ------------------------------------------------------------
# OBTÉM FILTROS DE TRADING (LOT_SIZE, MIN_NOTIONAL)
# ------------------------------------------------------------

def get_symbol_filters(symbol: str) -> dict:
    url = f"{BASE_URL}/api/v3/exchangeInfo"
    r = session.get(url, params={"symbol": f"{symbol}USDT"})

    if r.status_code != 200:
        raise Exception(f"Erro exchangeInfo: {r.text}")

    data = r.json()["symbols"][0]

    filters = {f["filterType"]: f for f in data["filters"]}
    return filters


# ------------------------------------------------------------
# AJUSTAR QUANTIDADE PARA LOT_SIZE
# ------------------------------------------------------------

def adjust_quantity_to_filters(symbol: str, qty: float) -> float:
    """
    Ajusta a quantidade conforme LOT_SIZE da Binance.
    """
    filters = get_symbol_filters(symbol)
    lot = filters.get("LOT_SIZE")
    if not lot:
        return qty

    step = lot["stepSize"]

    # stepSize pode ser string tipo "0.0001"
    decimals = 0
    if "." in step:
        decimals = len(step.split(".")[1].rstrip("0"))

    return float(f"{qty:.{decimals}f}")


# ------------------------------------------------------------
# ORDEM MARKET SELL
# ------------------------------------------------------------

def create_market_sell_order(symbol: str, quantity: float):
    symbol = f"{symbol.upper()}USDT"

    url = f"{BASE_URL}/api/v3/order"
    params = {
        "symbol": symbol,
        "side": "SELL",
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": int(time.time() * 1000),
    }

    signed = sign_request(params)
    r = session.post(url, params=signed)

    if r.status_code not in (200, 201):
        raise Exception(f"Erro MARKET SELL: {r.status_code} {r.text}")

    return r.json()


# ------------------------------------------------------------
# ORDEM MARKET BUY
# ------------------------------------------------------------

def create_market_buy_order(symbol: str, quote_usdt: float):
    symbol = f"{symbol.upper()}USDT"

    url = f"{BASE_URL}/api/v3/order"
    params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "quoteOrderQty": quote_usdt,
        "timestamp": int(time.time() * 1000),
    }

    signed = sign_request(params)
    r = session.post(url, params=signed)

    if r.status_code not in (200, 201):
        raise Exception(f"Erro MARKET BUY: {r.status_code} {r.text}")

    return r.json()


# ------------------------------------------------------------
# OBTÉM SALDO DE UMA MOEDA
# ------------------------------------------------------------

def get_account_balance(asset: str) -> float:
    url = f"{BASE_URL}/api/v3/account"
    params = {"timestamp": int(time.time() * 1000)}

    signed = sign_request(params)
    r = session.get(url, params=signed)

    if r.status_code != 200:
        raise Exception(f"Erro ao buscar conta: {r.text}")

    balances = r.json()["balances"]

    for b in balances:
        if b["asset"] == asset.upper():
            return float(b["free"])

    return 0.0


# ------------------------------------------------------------
# BUSCAR KLINES (CANDLES)
# ------------------------------------------------------------

def get_symbol_klines(symbol: str, interval="1h", limit=200):
    symbol = f"{symbol.upper()}USDT"

    url = f"{BASE_URL}/api/v3/klines"
    r = session.get(url, params={"symbol": symbol, "interval": interval, "limit": limit})

    if r.status_code != 200:
        logger.warning(f"Erro ao buscar klines de {symbol}: {r.text}")
        return []

    return r.json()


# ============================================================
# FIM DO ARQUIVO
# ============================================================
