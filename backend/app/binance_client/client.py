from functools import lru_cache
from datetime import datetime, timezone

from binance.spot import Spot

from app.core.config import get_settings


class BinanceClient:
    """
    Wrapper simples em cima do binance-connector.
    Por enquanto usamos apenas market data (klines 5m).
    """

    def __init__(self) -> None:
        settings = get_settings()
        # Para market data não precisamos de API key, mas já deixamos pronto
        if settings.BINANCE_API_KEY and settings.BINANCE_API_SECRET:
            self.client = Spot(
                api_key=settings.BINANCE_API_KEY,
                api_secret=settings.BINANCE_API_SECRET,
            )
        else:
            self.client = Spot()

    def get_klines_5m(self, symbol: str, limit: int = 200) -> list[dict]:
        """
        Busca candles 5m na Binance e retorna em formato normalizado.
        """
        raw = self.client.klines(symbol=symbol, interval="5m", limit=limit)
        candles: list[dict] = []
        for k in raw:
            open_time_ms = k[0]
            candles.append(
                {
                    "open_time": datetime.fromtimestamp(open_time_ms / 1000, tz=timezone.utc),
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                }
            )
        return candles


@lru_cache
def get_binance_client() -> BinanceClient:
    """
    Instância única (cacheada) do client.
    """
    return BinanceClient()
