from __future__ import annotations

from typing import List, Optional
from io import StringIO
import csv

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import Trade

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("/ping")
def trades_ping() -> dict:
    return {"message": "trades endpoint ok"}


@router.get("/recent")
def list_recent_trades(
    limit: int = Query(50, ge=1, le=500),
    bot_id: Optional[int] = None,
    symbol: Optional[str] = None,
    session: Session = Depends(get_session),
) -> List[Trade]:
    """
    Lista os trades mais recentes, opcionalmente filtrando por bot_id e/ou symbol.
    Ordena do mais recente para o mais antigo.
    """
    query = select(Trade)

    if bot_id is not None:
        query = query.where(Trade.bot_id == bot_id)

    if symbol is not None:
        symbol = symbol.upper().strip()
        query = query.where(Trade.symbol == symbol)

    query = query.order_by(Trade.id.desc()).limit(limit)

    trades = session.exec(query).all()
    return trades


@router.get("/export")
def export_trades_csv(
    limit: int = Query(200, ge=1, le=2000),
    bot_id: Optional[int] = None,
    symbol: Optional[str] = None,
    session: Session = Depends(get_session),
) -> StreamingResponse:
    """
    Exporta trades em formato CSV, com os mesmos filtros de /recent.
    """
    query = select(Trade)

    if bot_id is not None:
        query = query.where(Trade.bot_id == bot_id)

    if symbol is not None:
        symbol = symbol.upper().strip()
        query = query.where(Trade.symbol == symbol)

    # exporta ordenado do mais recente para o mais antigo
    query = query.order_by(Trade.id.desc()).limit(limit)
    trades = session.exec(query).all()

    output = StringIO()
    writer = csv.writer(output)

    # cabeçalho
    writer.writerow(
        [
            "id",
            "bot_id",
            "symbol",
            "side",
            "price",
            "qty",
            "quote_qty",
            "fee_amount",
            "fee_asset",
            "realized_pnl",
            "is_simulated",
            "info",
            "created_at",
        ]
    )

    # linhas
    for t in trades:
        writer.writerow(
            [
                t.id,
                t.bot_id,
                t.symbol,
                t.side,
                t.price,
                t.qty,
                t.quote_qty,
                t.fee_amount,
                t.fee_asset,
                t.realized_pnl,
                t.is_simulated,
                (t.info or ""),
                t.created_at.isoformat() if t.created_at else "",
            ]
        )

    output.seek(0)
    filename = "trades_export.csv"

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
