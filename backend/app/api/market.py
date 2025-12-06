import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.db.models import Candle, Indicator
from app.indicators.ta import compute_indicators
from app.binance_client.client import get_binance_client

router = APIRouter(prefix="/market", tags=["market"])


def normalize_symbol(symbol: str) -> str:
    """
    Converte formatos tipo 'BTC/USDT' para 'BTCUSDT', maiúsculo.
    """
    return symbol.replace("/", "").strip().upper()


@router.post("/sync/{symbol}")
def sync_symbol_data(
    symbol: str,
    limit: int = 200,
    session: Session = Depends(get_session),
) -> dict:
    """
    Sincroniza candles 5m e indicadores para um símbolo via Binance.
    - Busca até 'limit' candles recentes (padrão 200).
    - Atualiza tabelas Candle e Indicator.
    """
    norm_symbol = normalize_symbol(symbol)
    client = get_binance_client()

    try:
        candles_raw = client.get_klines_5m(norm_symbol, limit=limit)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao buscar candles na Binance para {norm_symbol}: {exc}",
        )

    if not candles_raw:
        raise HTTPException(
            status_code=400,
            detail=f"Nenhum candle retornado para {norm_symbol}",
        )

    # Insere candles novos (evita duplicados por open_time)
    inserted = 0
    for c in candles_raw:
        existing = session.exec(
            select(Candle).where(
                Candle.symbol == norm_symbol,
                Candle.open_time == c["open_time"],
            )
        ).first()
        if existing:
            continue

        candle = Candle(
            symbol=norm_symbol,
            open_time=c["open_time"],
            open=c["open"],
            high=c["high"],
            low=c["low"],
            close=c["close"],
            volume=c["volume"],
        )
        session.add(candle)
        inserted += 1

    session.commit()

    # Busca todos os candles desse símbolo para calcular indicadores
    candles = session.exec(
        select(Candle)
        .where(Candle.symbol == norm_symbol)
        .order_by(Candle.open_time)
    ).all()

    if not candles:
        raise HTTPException(
            status_code=500,
            detail=f"Não há candles salvos para {norm_symbol} após a sincronização.",
        )

    df = pd.DataFrame(
        [
            {
                "open_time": c.open_time,
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume,
            }
            for c in candles
        ]
    )

    df = compute_indicators(df)

    # Atualiza / cria os indicadores na tabela Indicator
    upserted = 0
    for row in df.itertuples(index=False):
        ind = session.exec(
            select(Indicator).where(
                Indicator.symbol == norm_symbol,
                Indicator.open_time == row.open_time,
            )
        ).first()

        if not ind:
            ind = Indicator(
                symbol=norm_symbol,
                open_time=row.open_time,
                close=row.close,
            )

        ind.close = float(row.close)
        ind.ema9 = float(row.ema9) if row.ema9 == row.ema9 else None
        ind.ema21 = float(row.ema21) if row.ema21 == row.ema21 else None
        ind.rsi14 = float(row.rsi14) if row.rsi14 == row.rsi14 else None
        ind.macd = float(row.macd) if row.macd == row.macd else None
        ind.macd_signal = (
            float(row.macd_signal) if row.macd_signal == row.macd_signal else None
        )
        ind.macd_hist = float(row.macd_hist) if row.macd_hist == row.macd_hist else None
        ind.adx = float(row.adx) if row.adx == row.adx else None
        ind.trend_score = (
            float(row.trend_score) if row.trend_score == row.trend_score else None
        )
        ind.trend_label = str(row.trend_label) if row.trend_label is not None else None
        ind.market_signal_compra = bool(row.market_signal_compra)
        ind.market_signal_venda = bool(row.market_signal_venda)

        session.add(ind)
        upserted += 1

    session.commit()

    return {
        "symbol": norm_symbol,
        "inserted_candles": inserted,
        "total_candles": len(candles),
        "upserted_indicators": upserted,
    }


@router.get("/indicators/{symbol}", response_model=list[Indicator])
def get_latest_indicators(
    symbol: str,
    limit: int = 10,
    session: Session = Depends(get_session),
) -> list[Indicator]:
    """
    Retorna os últimos 'limit' registros de indicadores para um símbolo.
    """
    norm_symbol = normalize_symbol(symbol)

    indicators = session.exec(
        select(Indicator)
        .where(Indicator.symbol == norm_symbol)
        .order_by(Indicator.open_time.desc())
        .limit(limit)
    ).all()

    # devolve em ordem cronológica crescente
    return list(reversed(indicators))
