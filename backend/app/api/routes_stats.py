from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.bot import Bot
from app.models.trade import Trade

router = APIRouter()


@router.get("/ping")
def stats_ping():
    return {"message": "stats endpoint ok"}


@router.get("/summary")
def get_stats_summary(session: Session = Depends(get_session)):
    """
    Resumo global dos bots (apenas leitura, baseado nos dados da BD).
    """
    bots = session.exec(select(Bot)).all()
    trades = session.exec(select(Trade)).all()

    total_bots = len(bots)
    total_bots_online = sum(1 for b in bots if b.status == "online")
    total_bots_blocked = sum(1 for b in bots if b.blocked)
    total_bots_with_open_position = sum(1 for b in bots if b.has_open_position)
    total_saldo_usdt_livre = sum(float(b.saldo_usdt_livre or 0) for b in bots)

    total_realized_pnl = 0.0
    total_fees_usdt = 0.0

    for t in trades:
        if t.realized_pnl is not None:
            total_realized_pnl += float(t.realized_pnl)
        if t.fee_amount is not None and t.fee_asset == "USDT":
            total_fees_usdt += float(t.fee_amount)

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
