from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.db.models import (
    Bot,
    BotStatus,
    BotPair,
    Indicator,
    SystemState,
    Trade,
    TradeSide,
)


# --------------------------------------------------------------------
# Helpers de acesso a dados
# --------------------------------------------------------------------


def _get_system_state(session: Session) -> SystemState:
    state = session.get(SystemState, 1)
    if not state:
        state = SystemState(id=1, online=False, simulation_mode=True)
        session.add(state)
        session.commit()
        session.refresh(state)
    return state


def _get_latest_indicators_map(
    session: Session,
    symbols: list[str],
) -> dict[str, Indicator]:
    result: dict[str, Indicator] = {}
    for symbol in symbols:
        ind = session.exec(
            select(Indicator)
            .where(Indicator.symbol == symbol)
            .order_by(Indicator.open_time.desc())
            .limit(1)
        ).first()
        if ind:
            result[symbol] = ind
    return result


def _indicator_snapshot(ind: Indicator) -> dict[str, Any]:
    return {
        "symbol": ind.symbol,
        "open_time": ind.open_time.isoformat(),
        "close": ind.close,
        "ema9": ind.ema9,
        "ema21": ind.ema21,
        "rsi14": ind.rsi14,
        "macd": ind.macd,
        "macd_signal": ind.macd_signal,
        "macd_hist": ind.macd_hist,
        "adx": ind.adx,
        "trend_score": ind.trend_score,
        "trend_label": ind.trend_label,
        "market_signal_compra": ind.market_signal_compra,
        "market_signal_venda": ind.market_signal_venda,
    }


# --------------------------------------------------------------------
# Regras de decisão
# --------------------------------------------------------------------


def _can_buy(
    bot: Bot,
    pair: BotPair,
    ind: Indicator,
    valor_atual: float,
    force_initial_buy: bool,
) -> tuple[bool, str]:
    """
    Aplica regras de compra para um par.
    Retorna (pode_comprar, motivo).
    """

    if bot.status != BotStatus.ONLINE:
        return False, "bot_not_online"

    if pair.has_open_position:
        return False, "already_has_position"

    if bot.saldo_usdt_livre < pair.valor_de_trade_usdt:
        return False, "insufficient_balance"

    # Compra forçada ao iniciar: ignora regras de % e de mercado.
    if force_initial_buy:
        return True, "comprar_ao_iniciar"

    # Regra de porcentagem_compra (sempre negativa quando usada)
    if pair.porcentagem_compra != 0 and pair.valor_inicial:
        var_pct = (valor_atual - pair.valor_inicial) / pair.valor_inicial * 100.0
        # Ex.: porcentagem_compra = -5 → só compra se var_pct <= -5
        if var_pct > pair.porcentagem_compra:
            return (
                False,
                f"var_pct={var_pct:.2f}% > limite_compra={pair.porcentagem_compra}%",
            )

    # Regra de compra_mercado (índice de tendência)
    if bot.compra_mercado:
        if not bool(ind.market_signal_compra):
            return False, "market_signal_compra_false"

    return True, "regras_compra_ok"


def _can_sell(
    bot: Bot,
    pair: BotPair,
    ind: Indicator,
    valor_atual: float,
) -> tuple[bool, str]:
    """
    Aplica regras de venda para um par.
    Retorna (pode_vender, motivo).
    """

    if bot.status != BotStatus.ONLINE:
        return False, "bot_not_online"

    if not pair.has_open_position or pair.qty_moeda <= 0:
        return False, "no_open_position"

    # Base para cálculo da %: valor_inicial ou last_buy_price
    base_price = pair.valor_inicial or pair.last_buy_price
    if base_price and pair.porcentagem_venda != 0:
        var_pct = (valor_atual - base_price) / base_price * 100.0
        # Ex.: porcentagem_venda = 5 → vende se var_pct >= 5
        if var_pct < pair.porcentagem_venda:
            return (
                False,
                f"var_pct={var_pct:.2f}% < limite_venda={pair.porcentagem_venda}%",
            )

    # Regra de venda_mercado (índice de tendência)
    if bot.venda_mercado:
        if not bool(ind.market_signal_venda):
            return False, "market_signal_venda_false"

    return True, "regras_venda_ok"


def _check_stop_loss_for_bot(
    bot: Bot,
    pairs: list[BotPair],
    indicators: dict[str, Indicator],
) -> bool:
    """
    Verifica se o stop loss do bot foi atingido em alguma posição.
    Regra (simplificada):
      - Para cada par com posição aberta,
      - Se variação vs last_buy_price <= stop_loss_percent (negativo),
      - Dispara stop do bot.
    """
    if bot.stop_loss_percent is None or bot.stop_loss_percent >= 0:
        return False

    for pair in pairs:
        if not pair.has_open_position or pair.qty_moeda <= 0:
            continue
        if not pair.last_buy_price:
            continue

        ind = indicators.get(pair.symbol)
        if not ind:
            continue

        valor_atual = ind.close
        var_pct = (valor_atual - pair.last_buy_price) / pair.last_buy_price * 100.0
        if var_pct <= bot.stop_loss_percent:
            return True

    return False


# --------------------------------------------------------------------
# Execução de trades simulados
# --------------------------------------------------------------------


def _execute_buy(
    session: Session,
    bot: Bot,
    pair: BotPair,
    ind: Indicator,
    valor_atual: float,
    motivo: str,
) -> dict[str, Any]:
    """
    Executa compra simulada de valor_de_trade_usdt, atualiza saldo e posição.
    """
    now = datetime.utcnow()

    valor_trade = pair.valor_de_trade_usdt

    # Verificação final de saldo
    if bot.saldo_usdt_livre < valor_trade:
        return {
            "symbol": pair.symbol,
            "action": "no_buy",
            "reason": "insufficient_balance_at_execution",
        }

    qty = valor_trade / valor_atual

    trade = Trade(
        bot_id=bot.id,
        bot_pair_id=pair.id,
        symbol=pair.symbol,
        side=TradeSide.BUY,
        qty=qty,
        price=valor_atual,
        value_usdt=valor_trade,
        fee_usdt=0.0,
        pnl_usdt=None,
        indicator_snapshot=json.dumps(_indicator_snapshot(ind)),
        rule_snapshot=motivo,
        binance_order_id=None,  # modo simulado
    )
    session.add(trade)

    # Atualiza estado do bot e do par
    bot.saldo_usdt_livre -= valor_trade
    bot.updated_at = now

    pair.has_open_position = True
    pair.qty_moeda = qty
    pair.last_buy_price = valor_atual
    pair.valor_inicial = valor_atual
    pair.updated_at = now

    session.add(bot)
    session.add(pair)

    return {
        "symbol": pair.symbol,
        "action": "BUY",
        "price": valor_atual,
        "qty": qty,
        "value_usdt": valor_trade,
        "reason": motivo,
    }


def _execute_sell(
    session: Session,
    bot: Bot,
    pair: BotPair,
    ind: Indicator,
    valor_atual: float,
    motivo: str,
) -> dict[str, Any]:
    """
    Executa venda simulada de toda a posição, atualiza saldo e posição.
    """
    now = datetime.utcnow()

    if not pair.has_open_position or pair.qty_moeda <= 0:
        return {
            "symbol": pair.symbol,
            "action": "no_sell",
            "reason": "no_open_position_at_execution",
        }

    qty = pair.qty_moeda
    value_usdt = qty * valor_atual

    cost_basis = 0.0
    if pair.last_buy_price:
        cost_basis = pair.last_buy_price * qty

    pnl = value_usdt - cost_basis if cost_basis > 0 else None

    trade = Trade(
        bot_id=bot.id,
        bot_pair_id=pair.id,
        symbol=pair.symbol,
        side=TradeSide.SELL,
        qty=qty,
        price=valor_atual,
        value_usdt=value_usdt,
        fee_usdt=0.0,
        pnl_usdt=pnl,
        indicator_snapshot=json.dumps(_indicator_snapshot(ind)),
        rule_snapshot=motivo,
        binance_order_id=None,  # modo simulado
    )
    session.add(trade)

    # Atualiza saldo do bot
    bot.saldo_usdt_livre += value_usdt
    bot.updated_at = now

    # Zera posição
    pair.has_open_position = False
    pair.qty_moeda = 0.0
    pair.last_sell_price = valor_atual
    pair.valor_inicial = valor_atual  # referência passa a ser o último preço da venda
    pair.updated_at = now

    session.add(bot)
    session.add(pair)

    return {
        "symbol": pair.symbol,
        "action": "SELL",
        "price": valor_atual,
        "qty": qty,
        "value_usdt": value_usdt,
        "pnl_usdt": pnl,
        "reason": motivo,
    }


# --------------------------------------------------------------------
# Função principal: roda 1 ciclo de decisão para 1 bot
# --------------------------------------------------------------------


def run_bot_cycle(session: Session, bot_id: int) -> dict[str, Any]:
    """
    Executa um ciclo de decisão para um bot (modo simulado):
    - verifica se o sistema está online
    - verifica se o bot está online
    - carrega pares e últimos indicadores
    - aplica stop loss (se disparar, vende tudo e bloqueia o bot)
    - aplica regras de compra/venda por par
    - registra trades simulados no banco
    """
    now = datetime.utcnow()
    system_state = _get_system_state(session)

    if not system_state.online:
        return {
            "bot_id": bot_id,
            "status": "system_offline",
            "message": "SystemState.online = False, nada executado.",
        }

    bot = session.get(Bot, bot_id)
    if not bot:
        return {
            "bot_id": bot_id,
            "status": "bot_not_found",
        }

    status_before = bot.status.value

    if bot.status != BotStatus.ONLINE:
        return {
            "bot_id": bot_id,
            "status": "bot_not_online",
            "bot_status": bot.status.value,
        }

    # Carrega pares do bot
    pairs = session.exec(
        select(BotPair).where(BotPair.bot_id == bot_id)
    ).all()
    if not pairs:
        return {
            "bot_id": bot_id,
            "status": "no_pairs",
            "message": "Bot não tem pares configurados.",
        }

    symbols = list({p.symbol for p in pairs})
    indicators_map = _get_latest_indicators_map(session, symbols)

    actions: list[dict[str, Any]] = []

    # 1) Verifica stop loss
    stop_triggered = _check_stop_loss_for_bot(bot, pairs, indicators_map)
    if stop_triggered:
        # Vende todas as posições abertas e bloqueia o bot
        for pair in pairs:
            ind = indicators_map.get(pair.symbol)
            if not ind:
                actions.append(
                    {
                        "symbol": pair.symbol,
                        "action": "skip_stop_loss",
                        "reason": "no_indicator_for_symbol",
                    }
                )
                continue

            if not pair.has_open_position or pair.qty_moeda <= 0:
                actions.append(
                    {
                        "symbol": pair.symbol,
                        "action": "skip_stop_loss",
                        "reason": "no_open_position",
                    }
                )
                continue

            valor_atual = ind.close
            result = _execute_sell(
                session=session,
                bot=bot,
                pair=pair,
                ind=ind,
                valor_atual=valor_atual,
                motivo="stop_loss_triggered",
            )
            actions.append(result)

        bot.status = BotStatus.BLOCKED
        bot.updated_at = now
        session.add(bot)
        session.commit()

        return {
            "bot_id": bot_id,
            "status_before": status_before,
            "status_after": bot.status.value,
            "stop_loss_triggered": True,
            "actions": actions,
        }

    # 2) Sem stop loss, aplica regras de compra/venda
    for pair in pairs:
        ind = indicators_map.get(pair.symbol)
        if not ind:
            actions.append(
                {
                    "symbol": pair.symbol,
                    "action": "skip",
                    "reason": "no_indicator_for_symbol",
                }
            )
            continue

        valor_atual = ind.close

        # Compra/venda normal
        if pair.has_open_position:
            # Verifica se pode vender
            can_sell, reason = _can_sell(
                bot=bot,
                pair=pair,
                ind=ind,
                valor_atual=valor_atual,
            )
            if can_sell:
                result = _execute_sell(
                    session=session,
                    bot=bot,
                    pair=pair,
                    ind=ind,
                    valor_atual=valor_atual,
                    motivo=reason,
                )
                actions.append(result)
            else:
                actions.append(
                    {
                        "symbol": pair.symbol,
                        "action": "hold",
                        "reason": reason,
                    }
                )
        else:
            # Verifica se é compra ao iniciar (forçada)
            force_initial_buy = bool(
                bot.comprar_ao_iniciar and not pair.has_open_position and pair.valor_inicial is None
            )

            can_buy, reason = _can_buy(
                bot=bot,
                pair=pair,
                ind=ind,
                valor_atual=valor_atual,
                force_initial_buy=force_initial_buy,
            )

            if can_buy:
                result = _execute_buy(
                    session=session,
                    bot=bot,
                    pair=pair,
                    ind=ind,
                    valor_atual=valor_atual,
                    motivo=reason,
                )
                actions.append(result)
            else:
                # Se ainda não temos valor_inicial definido, registramos o preço
                if pair.valor_inicial is None:
                    pair.valor_inicial = valor_atual
                    pair.updated_at = now
                    session.add(pair)

                actions.append(
                    {
                        "symbol": pair.symbol,
                        "action": "no_buy",
                        "reason": reason,
                    }
                )

    bot.updated_at = now
    session.add(bot)
    session.commit()

    return {
        "bot_id": bot_id,
        "status_before": status_before,
        "status_after": bot.status.value,
        "stop_loss_triggered": False,
        "actions": actions,
    }
