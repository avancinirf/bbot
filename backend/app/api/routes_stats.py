from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import Bot, Trade

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/ping")
def stats_ping() -> dict:
    return {"message": "stats endpoint ok"}


@router.get("/summary")
def stats_summary(db: Session = Depends(get_session)) -> dict:
    """Resumo global dos bots e trades."""
    bots: List[Bot] = db.exec(select(Bot)).all()
    trades: List[Trade] = db.exec(select(Trade)).all()

    total_bots = len(bots)
    total_bots_online = sum(1 for b in bots if b.status == "online")
    total_bots_blocked = sum(1 for b in bots if b.blocked)
    total_bots_with_open_position = sum(1 for b in bots if b.has_open_position)

    total_saldo_usdt_livre = sum(float(b.saldo_usdt_livre or 0) for b in bots)

    total_realized_pnl = sum(
        float(t.realized_pnl or 0)
        for t in trades
        if t.realized_pnl is not None
    )

    total_fees_usdt = sum(
        float(t.fee_amount or 0)
        for t in trades
        if t.fee_amount is not None and t.fee_asset == "USDT"
    )

    return {
        "total_bots": total_bots,
        "total_bots_online": total_bots_online,
        "total_bots_blocked": total_bots_blocked,
        "total_bots_with_open_position": total_bots_with_open_position,
        "total_saldo_usdt_livre": total_saldo_usdt_livre,
        "total_realized_pnl": total_realized_pnl,
        "total_fees_usdt": total_fees_usdt,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/by_bot")
def stats_by_bot(db: Session = Depends(get_session)) -> list[dict]:
    """Resumo de performance por bot."""
    bots: List[Bot] = db.exec(select(Bot)).all()
    result: list[dict] = []

    for bot in bots:
        trades: List[Trade] = db.exec(
            select(Trade).where(Trade.bot_id == bot.id)
        ).all()

        # ordena em memória para pegar o último trade
        trades.sort(key=lambda t: t.created_at or datetime.min)

        num_trades = len(trades)
        num_buys = sum(1 for t in trades if t.side == "BUY")
        num_sells = sum(1 for t in trades if t.side == "SELL")

        realized_pnl = sum(
            float(t.realized_pnl or 0)
            for t in trades
            if t.realized_pnl is not None
        )

        total_fees_usdt = sum(
            float(t.fee_amount or 0)
            for t in trades
            if t.fee_amount is not None and t.fee_asset == "USDT"
        )

        last_trade_at = trades[-1].created_at if trades else None

        result.append(
            {
                "bot_id": bot.id,
                "bot_name": bot.name,
                "symbol": bot.symbol,
                "num_trades": num_trades,
                "num_buys": num_buys,
                "num_sells": num_sells,
                "realized_pnl": realized_pnl,
                "total_fees_usdt": total_fees_usdt,
                "last_trade_at": last_trade_at,
            }
        )

    return result
