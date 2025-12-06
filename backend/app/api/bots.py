from datetime import datetime
from typing import Optional, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, SQLModel, select

from app.db.session import get_session
from app.db.models import Bot, BotStatus, BotPair, Trade, Indicator

from app.bots.engine import run_bot_cycle


router = APIRouter(prefix="/bots", tags=["bots"])

AVAILABLE_PAIRS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "XLM/USDT",
    "ASTR/USDT", "SUI/USDT", "ADA/USDT", "NEAR/USDT", "APT/USDT",
    "FET/USDT", "LINK/USDT", "AVAX/USDT", "HBAR/USDT", "BCH/USDT",
    "DOGE/USDT", "AAVE/USDT", "ENA/USDT", "ZEC/USDT", "DASH/USDT",
]



# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------


def normalize_symbol(symbol: str) -> str:
    """
    Converte formatos tipo 'BTC/USDT' para 'BTCUSDT', maiúsculo.
    """
    return symbol.replace("/", "").strip().upper()


@router.get("/available_pairs", response_model=list[str])
def get_available_pairs() -> list[str]:
    """
    Lista estática de pares disponíveis para configurar nos bots.
    """
    return AVAILABLE_PAIRS


# --------------------------------------------------------------------
# Schemas para entrada/saída
# --------------------------------------------------------------------


class BotCreate(SQLModel):
    name: str
    saldo_usdt_limit: float = 0.0
    stop_loss_percent: float = -20.0
    comprar_ao_iniciar: bool = False
    compra_mercado: bool = True
    venda_mercado: bool = True


class BotUpdate(SQLModel):
    name: Optional[str] = None
    saldo_usdt_limit: Optional[float] = None
    stop_loss_percent: Optional[float] = None
    comprar_ao_iniciar: Optional[bool] = None
    compra_mercado: Optional[bool] = None
    venda_mercado: Optional[bool] = None


class BotStatusUpdate(SQLModel):
    status: BotStatus


class BotPairCreate(SQLModel):
    symbol: str
    valor_de_trade_usdt: float = 10.0
    porcentagem_compra: float = 0.0
    porcentagem_venda: float = 0.0


class BotPairUpdate(SQLModel):
    valor_de_trade_usdt: Optional[float] = None
    porcentagem_compra: Optional[float] = None
    porcentagem_venda: Optional[float] = None


# --------------------------------------------------------------------
# Rotas de bots
# --------------------------------------------------------------------


@router.get("", response_model=list[Bot])
def list_bots(session: Session = Depends(get_session)) -> list[Bot]:
    """
    Lista todos os bots cadastrados.
    """
    bots = session.exec(select(Bot)).all()
    return bots


@router.post("", response_model=Bot, status_code=201)
def create_bot(payload: BotCreate, session: Session = Depends(get_session)) -> Bot:
    """
    Cria um novo bot.
    saldo_usdt_livre começa igual ao saldo_usdt_limit.
    """
    bot = Bot(
        name=payload.name,
        status=BotStatus.OFFLINE,
        saldo_usdt_limit=payload.saldo_usdt_limit,
        saldo_usdt_livre=payload.saldo_usdt_limit,
        stop_loss_percent=payload.stop_loss_percent,
        comprar_ao_iniciar=payload.comprar_ao_iniciar,
        compra_mercado=payload.compra_mercado,
        venda_mercado=payload.venda_mercado,
    )
    session.add(bot)
    session.commit()
    session.refresh(bot)
    return bot


@router.get("/{bot_id}", response_model=Bot)
def get_bot(bot_id: int, session: Session = Depends(get_session)) -> Bot:
    """
    Detalhes de um bot específico (sem pares ainda).
    """
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")
    return bot


@router.put("/{bot_id}", response_model=Bot)
def update_bot(
    bot_id: int,
    payload: BotUpdate,
    session: Session = Depends(get_session),
) -> Bot:
    """
    Atualiza campos básicos do bot.
    Se o limite de saldo for reduzido e o saldo livre ficar maior que o limite,
    o saldo livre é ajustado para o novo limite.
    """
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")

    if payload.name is not None:
        bot.name = payload.name
    if payload.saldo_usdt_limit is not None:
        bot.saldo_usdt_limit = payload.saldo_usdt_limit
        if bot.saldo_usdt_livre > bot.saldo_usdt_limit:
            bot.saldo_usdt_livre = bot.saldo_usdt_limit
    if payload.stop_loss_percent is not None:
        bot.stop_loss_percent = payload.stop_loss_percent
    if payload.comprar_ao_iniciar is not None:
        bot.comprar_ao_iniciar = payload.comprar_ao_iniciar
    if payload.compra_mercado is not None:
        bot.compra_mercado = payload.compra_mercado
    if payload.venda_mercado is not None:
        bot.venda_mercado = payload.venda_mercado

    bot.updated_at = datetime.utcnow()
    session.add(bot)
    session.commit()
    session.refresh(bot)
    return bot


@router.post("/{bot_id}/status", response_model=Bot)
def set_bot_status(
    bot_id: int,
    payload: BotStatusUpdate,
    session: Session = Depends(get_session),
) -> Bot:
    """
    Altera o status de um bot:
    - online
    - offline
    - blocked
    """
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")

    bot.status = payload.status
    bot.updated_at = datetime.utcnow()
    session.add(bot)
    session.commit()
    session.refresh(bot)
    return bot


@router.post("/block_all")
def block_all_bots(session: Session = Depends(get_session)) -> dict:
    """
    Bloqueia todos os bots (status = blocked).
    """
    bots = session.exec(select(Bot)).all()
    count = 0
    for bot in bots:
        if bot.status != BotStatus.BLOCKED:
            bot.status = BotStatus.BLOCKED
            bot.updated_at = datetime.utcnow()
            session.add(bot)
            count += 1
    session.commit()
    return {"blocked": count}


@router.post("/unblock_all")
def unblock_all_bots(session: Session = Depends(get_session)) -> dict:
    """
    Desbloqueia todos os bots bloqueados (voltam para offline).
    """
    bots = session.exec(select(Bot)).all()
    count = 0
    for bot in bots:
        if bot.status == BotStatus.BLOCKED:
            bot.status = BotStatus.OFFLINE
            bot.updated_at = datetime.utcnow()
            session.add(bot)
            count += 1
    session.commit()
    return {"unblocked": count}


# --------------------------------------------------------------------
# Rotas de pares (moedas) do bot
# --------------------------------------------------------------------


@router.get("/{bot_id}/pairs", response_model=list[BotPair])
def list_pairs(bot_id: int, session: Session = Depends(get_session)) -> list[BotPair]:
    """
    Lista os pares configurados para um bot.
    """
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")

    pairs = session.exec(
        select(BotPair).where(BotPair.bot_id == bot_id)
    ).all()
    return pairs


@router.post("/{bot_id}/pairs", response_model=BotPair, status_code=201)
def add_pair(
    bot_id: int,
    payload: BotPairCreate,
    session: Session = Depends(get_session),
) -> BotPair:
    """
    Adiciona um novo par a um bot.
    Evita duplicar o mesmo símbolo no mesmo bot.
    """
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")

    symbol_norm = normalize_symbol(payload.symbol)

    # Verifica se já existe esse par nesse bot
    existing = session.exec(
        select(BotPair).where(
            BotPair.bot_id == bot_id,
            BotPair.symbol == symbol_norm,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Esse par já existe para este bot",
        )

    pair = BotPair(
        bot_id=bot_id,
        symbol=symbol_norm,
        valor_de_trade_usdt=payload.valor_de_trade_usdt,
        porcentagem_compra=payload.porcentagem_compra,
        porcentagem_venda=payload.porcentagem_venda,
    )
    session.add(pair)
    session.commit()
    session.refresh(pair)
    return pair


@router.put("/pairs/{pair_id}", response_model=BotPair)
def update_pair(
    pair_id: int,
    payload: BotPairUpdate,
    session: Session = Depends(get_session),
) -> BotPair:
    """
    Atualiza configuração de um par:
    - valor_de_trade_usdt
    - porcentagem_compra
    - porcentagem_venda
    """
    pair = session.get(BotPair, pair_id)
    if not pair:
        raise HTTPException(status_code=404, detail="Par não encontrado")

    if payload.valor_de_trade_usdt is not None:
        pair.valor_de_trade_usdt = payload.valor_de_trade_usdt
    if payload.porcentagem_compra is not None:
        pair.porcentagem_compra = payload.porcentagem_compra
    if payload.porcentagem_venda is not None:
        pair.porcentagem_venda = payload.porcentagem_venda

    pair.updated_at = datetime.utcnow()
    session.add(pair)
    session.commit()
    session.refresh(pair)
    return pair


# --------------------------------------------------------------------
# Execução de 1 ciclo do bot (modo simulado)
# --------------------------------------------------------------------


@router.post("/{bot_id}/run_cycle")
def run_cycle(
    bot_id: int,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Executa 1 ciclo de decisão do bot (compra/venda/stop) em modo simulado.
    - Usa os indicadores mais recentes já salvos na base.
    - Atualiza saldo virtual, posições e registra trades.
    """
    result = run_bot_cycle(session, bot_id)
    return result


@router.get("/{bot_id}/trades", response_model=list[Trade])
def list_trades(
    bot_id: int,
    limit: int = 50,
    session: Session = Depends(get_session),
) -> list[Trade]:
    """
    Lista os últimos 'limit' trades de um bot (mais recentes primeiro).
    """
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")

    trades = session.exec(
        select(Trade)
        .where(Trade.bot_id == bot_id)
        .order_by(Trade.created_at.desc())
        .limit(limit)
    ).all()
    return trades

@router.get("/{bot_id}/status")
def get_bot_status(
    bot_id: int,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Retorna um status detalhado do bot:
    - dados do bot
    - pares configurados
    - último indicador/close por par
    - variação vs valor_inicial
    - resumo de equity (saldo + posições)
    """
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")

    # Carrega pares do bot
    pairs = session.exec(
        select(BotPair).where(BotPair.bot_id == bot_id)
    ).all()

    symbols = list({p.symbol for p in pairs})
    indicators_map: dict[str, Indicator] = {}

    # Busca o último indicador para cada símbolo
    for symbol in symbols:
        ind = session.exec(
            select(Indicator)
            .where(Indicator.symbol == symbol)
            .order_by(Indicator.open_time.desc())
            .limit(1)
        ).first()
        if ind:
            indicators_map[symbol] = ind

    pairs_status: list[dict[str, Any]] = []

    total_position_value_usdt = 0.0
    total_cost_basis_usdt = 0.0

    for pair in pairs:
        ind = indicators_map.get(pair.symbol)
        valor_atual: float | None = ind.close if ind else None

        var_pct_vs_valor_inicial: float | None = None
        if valor_atual is not None and pair.valor_inicial:
            var_pct_vs_valor_inicial = (
                (valor_atual - pair.valor_inicial) / pair.valor_inicial * 100.0
            )

        position_value = 0.0
        cost_basis = 0.0
        unrealized_pnl = None

        if (
            pair.has_open_position
            and pair.qty_moeda > 0
            and valor_atual is not None
        ):
            position_value = pair.qty_moeda * valor_atual
            total_position_value_usdt += position_value

            if pair.last_buy_price:
                cost_basis = pair.last_buy_price * pair.qty_moeda
                total_cost_basis_usdt += cost_basis
                unrealized_pnl = position_value - cost_basis

        pair_info = {
            "pair_id": pair.id,
            "symbol": pair.symbol,
            "valor_de_trade_usdt": pair.valor_de_trade_usdt,
            "valor_inicial": pair.valor_inicial,
            "porcentagem_compra": pair.porcentagem_compra,
            "porcentagem_venda": pair.porcentagem_venda,
            "has_open_position": pair.has_open_position,
            "qty_moeda": pair.qty_moeda,
            "last_buy_price": pair.last_buy_price,
            "last_sell_price": pair.last_sell_price,
            "valor_atual": valor_atual,
            "var_pct_vs_valor_inicial": var_pct_vs_valor_inicial,
            "unrealized_position_value_usdt": position_value,
            "unrealized_pnl_usdt": unrealized_pnl,
            "indicator": {
                "open_time": ind.open_time.isoformat() if ind else None,
                "close": ind.close if ind else None,
                "ema9": ind.ema9 if ind else None,
                "ema21": ind.ema21 if ind else None,
                "rsi14": ind.rsi14 if ind else None,
                "macd": ind.macd if ind else None,
                "macd_signal": ind.macd_signal if ind else None,
                "macd_hist": ind.macd_hist if ind else None,
                "adx": ind.adx if ind else None,
                "trend_score": ind.trend_score if ind else None,
                "trend_label": ind.trend_label if ind else None,
                "market_signal_compra": ind.market_signal_compra if ind else None,
                "market_signal_venda": ind.market_signal_venda if ind else None,
            } if ind else None,
        }

        pairs_status.append(pair_info)

    total_equity_usdt = bot.saldo_usdt_livre + total_position_value_usdt
    unrealized_pnl_total = None
    if total_cost_basis_usdt > 0:
        unrealized_pnl_total = total_position_value_usdt - total_cost_basis_usdt

    summary = {
        "saldo_usdt_limit": bot.saldo_usdt_limit,
        "saldo_usdt_livre": bot.saldo_usdt_livre,
        "total_position_value_usdt": total_position_value_usdt,
        "total_equity_usdt": total_equity_usdt,
        "unrealized_pnl_usdt": unrealized_pnl_total,
    }

    return {
        "bot": bot,
        "summary": summary,
        "pairs": pairs_status,
    }
