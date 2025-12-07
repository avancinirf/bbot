from __future__ import annotations

from datetime import datetime
from typing import List
import httpx

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.bot import Bot, BotCreate, BotRead
from app.models.trade import Trade, TradeRead
from app.binance.client import (
    validate_symbol as binance_validate_symbol,
    get_symbol_price,
)
from app.core.config import get_settings
from app.engine.runner import simulate_sell


router = APIRouter(prefix="/bots", tags=["bots"])


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def _get_bot_or_404(bot_id: int, session: Session) -> Bot:
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot id={bot_id} não encontrado.",
        )
    return bot


# ---------------------------------------------------------------------
# Endpoints básicos
# ---------------------------------------------------------------------
@router.get("/ping")
def ping_bots() -> dict:
    """Endpoint simples só para testar se o router /bots está ativo."""
    return {"message": "bots endpoint ok"}


@router.get("/", response_model=List[BotRead])
def list_bots(session: Session = Depends(get_session)) -> List[Bot]:
    """Lista todos os bots cadastrados (por enquanto, sem filtros)."""
    try:
        bots = session.exec(select(Bot)).all()
        return bots
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar bots: {e.__class__.__name__}: {e}",
        )

@router.get("/{bot_id}", response_model=BotRead)
def get_bot(bot_id: int, session: Session = Depends(get_session)) -> Bot:
    """
    Retorna os dados de um único bot pelo id.
    """
    bot = _get_bot_or_404(bot_id, session)
    return bot


@router.post("/", response_model=BotRead, status_code=status.HTTP_201_CREATED)
def create_bot(bot_in: BotCreate, session: Session = Depends(get_session)) -> Bot:
    """
    Cria um novo bot (começa offline, desbloqueado e com saldo_usdt_livre = saldo_usdt_limit).
    Não permite dois bots com o mesmo nome.
    Valida se o símbolo existe na Binance.
    """
    try:
        # Normaliza símbolo
        symbol = bot_in.symbol.upper().strip()

        # Validação de símbolo na Binance
        if not binance_validate_symbol(symbol):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Símbolo '{symbol}' não existe ou não está disponível na Binance.",
            )

        # Validação simples: nome único
        existing = session.exec(select(Bot).where(Bot.name == bot_in.name)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um bot com esse nome.",
            )

        data = bot_in.model_dump()
        data["symbol"] = symbol  # salva normalizado em maiúsculo
        bot = Bot(**data)

        # Regras iniciais
        bot.status = "offline"
        bot.blocked = False
        bot.saldo_usdt_livre = bot.saldo_usdt_limit

        session.add(bot)
        session.commit()
        session.refresh(bot)

        return bot
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar bot: {e.__class__.__name__}: {e}",
        )



# ---------------------------------------------------------------------
# Ações em um único bot: ligar/desligar/bloquear/desbloquear/remover
# ---------------------------------------------------------------------
@router.post("/{bot_id}/start", response_model=BotRead)
def start_bot(bot_id: int, session: Session = Depends(get_session)) -> Bot:
    """
    Coloca o bot online.
    Regras:
      - Não pode estar bloqueado (blocked = True).
      - Se já está online, apenas retorna o estado atual.
      - Se nunca foi iniciado, define started_at.
    """
    bot = _get_bot_or_404(bot_id, session)

    if bot.blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bot está bloqueado e não pode ser colocado online.",
        )

    if bot.status == "online":
        return bot

    bot.status = "online"
    if bot.started_at is None:
        bot.started_at = datetime.utcnow()

    session.add(bot)
    session.commit()
    session.refresh(bot)
    return bot


@router.post("/{bot_id}/stop", response_model=BotRead)
def stop_bot(bot_id: int, session: Session = Depends(get_session)) -> Bot:
    """
    Coloca o bot offline.
    Se já estiver offline, apenas retorna.
    """
    bot = _get_bot_or_404(bot_id, session)

    if bot.status == "offline":
        return bot

    bot.status = "offline"
    session.add(bot)
    session.commit()
    session.refresh(bot)
    return bot


@router.post("/{bot_id}/block", response_model=BotRead)
def block_bot(bot_id: int, session: Session = Depends(get_session)) -> Bot:
    """
    Bloqueia o bot.
    Regras:
      - blocked = True
      - status = offline (bot não roda mais)
    """
    bot = _get_bot_or_404(bot_id, session)

    bot.blocked = True
    bot.status = "offline"

    session.add(bot)
    session.commit()
    session.refresh(bot)
    return bot


@router.post("/{bot_id}/unblock", response_model=BotRead)
def unblock_bot(bot_id: int, session: Session = Depends(get_session)) -> Bot:
    """
    Desbloqueia o bot.
    Não altera o status (continua online/offline como está),
    mas pela nossa regra prática ele sempre estará offline,
    pois bloqueio sempre o deixa offline.
    """
    bot = _get_bot_or_404(bot_id, session)

    if not bot.blocked:
        return bot

    bot.blocked = False

    session.add(bot)
    session.commit()
    session.refresh(bot)
    return bot


@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bot(bot_id: int, session: Session = Depends(get_session)) -> None:
    """
    Remove o bot e tudo que temos sobre ele.
    Por enquanto só temos o registro na tabela bots.
    Futuramente, quando tivermos tabelas de trades/logs, vamos apagar tudo relacionado.
    """
    bot = _get_bot_or_404(bot_id, session)

    session.delete(bot)
    session.commit()
    # 204 No Content -> corpo vazio
    return None


# ---------------------------------------------------------------------
# Ações em massa: ligar/desligar todos
# ---------------------------------------------------------------------
@router.post("/actions/start_all")
def start_all_bots(session: Session = Depends(get_session)) -> dict:
    """
    Coloca online todos os bots que:
      - não estão bloqueados
      - estão offline
    Retorna quantos foram alterados.
    """
    bots = session.exec(select(Bot)).all()
    updated = 0

    for bot in bots:
        if not bot.blocked and bot.status != "online":
            bot.status = "online"
            if bot.started_at is None:
                bot.started_at = datetime.utcnow()
            updated += 1
            session.add(bot)

    if updated > 0:
        session.commit()

    return {"updated": updated}


@router.post("/actions/stop_all")
def stop_all_bots(session: Session = Depends(get_session)) -> dict:
    """
    Coloca offline todos os bots que estão online (independente de bloqueio).
    Retorna quantos foram alterados.
    """
    bots = session.exec(select(Bot)).all()
    updated = 0

    for bot in bots:
        if bot.status != "offline":
            bot.status = "offline"
            updated += 1
            session.add(bot)

    if updated > 0:
        session.commit()

    return {"updated": updated}


@router.get("/{bot_id}/trades", response_model=List[TradeRead])
def list_bot_trades(bot_id: int, session: Session = Depends(get_session)) -> List[Trade]:
    """
    Lista os trades de um bot, em ordem de criação.
    """
    bot = _get_bot_or_404(bot_id, session)
    trades = session.exec(
        select(Trade).where(Trade.bot_id == bot.id).order_by(Trade.id)
    ).all()
    return trades


@router.post("/{bot_id}/close_position", response_model=BotRead)
def close_position(bot_id: int, session: Session = Depends(get_session)) -> Bot:
    """
    Fecha manualmente a posição do bot, vendendo tudo ao preço de mercado atual.
    Não bloqueia o bot, diferente do stop-loss.
    """
    bot = _get_bot_or_404(bot_id, session)

    if not bot.has_open_position or bot.qty_moeda <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bot não possui posição aberta para fechar.",
        )

    try:
        price = get_symbol_price(bot.symbol)
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao obter preço atual na Binance: {str(e)}",
        )

    settings = get_settings()
    # Reutiliza a mesma lógica de venda simulada do engine
    simulate_sell(bot, session, settings, price, reason="manual_close")
    session.refresh(bot)
    return bot
