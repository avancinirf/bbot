from __future__ import annotations

import asyncio
from datetime import datetime

import httpx
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.state import get_system_running
from app.db.session import engine
from app.models.bot import Bot
from app.models.trade import Trade
from app.models.indicator import Indicator
from app.binance.client import get_symbol_price
from app.indicators.service import sync_indicators_for_symbol


ENGINE_INTERVAL_SECONDS = 5  # tempo entre ciclos do engine (pode ajustar depois)
INDICATOR_SYNC_MIN_INTERVAL_SECONDS = 60  # mínimo de 60s entre syncs por símbolo

# memória local do processo: última vez que sincronizamos indicadores por símbolo
_last_indicator_sync_by_symbol: dict[str, datetime] = {}


def get_latest_indicator_for_symbol(
    session: Session,
    symbol: str,
    interval: str = "5m",
) -> Indicator | None:
    """
    Busca o último indicador salvo para o símbolo/intervalo.
    Pode retornar None (sem dados ainda).
    """
    return session.exec(
        select(Indicator)
        .where(Indicator.symbol == symbol, Indicator.interval == interval)
        .order_by(Indicator.close_time.desc())
    ).first()


async def bot_engine_loop() -> None:
    """
    Loop principal do engine de bots.
    Roda em background e respeita o estado global system_running.
    """
    settings = get_settings()
    print(
        f"[ENGINE] Iniciando loop do engine (modo={settings.app_mode}, "
        f"intervalo={ENGINE_INTERVAL_SECONDS}s)"
    )

    while True:
        try:
            await run_engine_cycle()
        except Exception as e:
            print(f"[ENGINE] ERRO no ciclo: {e.__class__.__name__}: {e}")
        await asyncio.sleep(ENGINE_INTERVAL_SECONDS)


async def run_engine_cycle() -> None:
    """
    Um ciclo do engine:
    - Se o sistema estiver desligado, não faz nada.
    - Se ligado, busca bots online e não bloqueados e aplica a lógica.
    - Antes de processar bots, sincroniza indicadores 5m para cada símbolo,
      respeitando um intervalo mínimo entre syncs.
    """
    if not get_system_running():
        return

    settings = get_settings()
    now_dt = datetime.utcnow()
    now = now_dt.isoformat(timespec="seconds")
    print(f"[ENGINE] Ciclo iniciado em {now} (UTC)")

    with Session(engine) as session:
        bots = session.exec(
            select(Bot).where(
                Bot.status == "online",
                Bot.blocked == False,  # noqa: E712
            )
        ).all()

        if not bots:
            print("[ENGINE] Nenhum bot elegível (online e não bloqueado).")
            return

        # --- sincroniza indicadores por símbolo (uma vez a cada X segundos) ---
        symbols = sorted({bot.symbol for bot in bots})
        for symbol in symbols:
            last_sync = _last_indicator_sync_by_symbol.get(symbol)
            delta_ok = (
                not last_sync
                or (now_dt - last_sync).total_seconds()
                >= INDICATOR_SYNC_MIN_INTERVAL_SECONDS
            )

            if not delta_ok:
                continue

            try:
                inserted = sync_indicators_for_symbol(
                    symbol=symbol,
                    interval="5m",
                    limit=200,
                )
                _last_indicator_sync_by_symbol[symbol] = now_dt
                print(
                    f"[ENGINE] Indicadores sincronizados para {symbol}: "
                    f"inserted={inserted}"
                )
            except Exception as e:
                print(
                    f"[ENGINE] ERRO ao sincronizar indicadores para {symbol}: "
                    f"{e.__class__.__name__}: {e}"
                )

        print(f"[ENGINE] Encontrados {len(bots)} bot(s) elegível(is) para este ciclo:")

        for bot in bots:
            try:
                price = get_symbol_price(bot.symbol)
            except httpx.HTTPError as e:
                print(
                    f"[ENGINE] Erro HTTP ao obter preço de {bot.symbol} "
                    f"para bot id={bot.id}: {e}"
                )
                continue
            except Exception as e:
                print(
                    f"[ENGINE] Erro inesperado ao obter preço de {bot.symbol} "
                    f"para bot id={bot.id}: {e}"
                )
                continue

            indicator = get_latest_indicator_for_symbol(session, bot.symbol)

            print(
                f"  - Bot id={bot.id} name={bot.name} symbol={bot.symbol} "
                f"price_atual={price} saldo_livre={bot.saldo_usdt_livre} "
                f"has_open_position={bot.has_open_position} "
                f"indicator_ok={indicator is not None}"
            )

            process_bot_cycle(bot, session, settings, price, indicator)


def process_bot_cycle(
    bot: Bot,
    session: Session,
    settings,
    price: float,
    indicator: Indicator | None,
) -> None:
    """
    Decide o que fazer com o bot neste ciclo:
    - Se tem posição aberta → checa stop-loss e take profit.
    - Se NÃO tem posição aberta → aplica comprar_ao_iniciar / porcentagem_compra.
    """
    if bot.has_open_position:
        handle_position(bot, session, settings, price, indicator)
    else:
        handle_no_position(bot, session, settings, price, indicator)


def handle_no_position(
    bot: Bot,
    session: Session,
    settings,
    price: float,
    indicator: Indicator | None,
) -> None:
    """
    Sem posição aberta:
    - Se nunca fez trade e comprar_ao_iniciar = True → compra inicial
      (opcionalmente respeitando compra_mercado + market_signal_compra).
    - Caso contrário, se porcentagem_compra > 0 → compra quando cair X% abaixo
      do valor_inicial (opcionalmente respeitando compra_mercado + market_signal_compra).
    """
    has_trades = (
        session.exec(select(Trade.id).where(Trade.bot_id == bot.id)).first()
        is not None
    )

    # 1) Primeira entrada: comprar_ao_iniciar
    if (not has_trades) and bot.comprar_ao_iniciar:
        if bot.compra_mercado:
            if indicator is None or indicator.market_signal_compra is not True:
                print(
                    f"[ENGINE] Bot id={bot.id} comprar_ao_iniciar=True, "
                    "mas market_signal_compra não é True ou não há indicador. "
                    "Ignorando compra inicial."
                )
                return

        print(
            f"[ENGINE] Bot id={bot.id} sem trades anteriores e "
            f"comprar_ao_iniciar=True → executando COMPRA inicial."
        )
        simulate_buy(bot, session, settings, price)
        return

    # 2) Reentradas / entradas via porcentagem_compra
    perc_compra = bot.porcentagem_compra or 0.0
    if perc_compra > 0:
        # Se ainda não temos valor_inicial, definimos agora e esperamos queda
        if bot.valor_inicial is None:
            bot.valor_inicial = price
            session.add(bot)
            session.commit()
            session.refresh(bot)
            print(
                f"[ENGINE] Bot id={bot.id} definindo valor_inicial={price} "
                f"para regras de porcentagem_compra."
            )
            return

        var_pct = (price - bot.valor_inicial) / bot.valor_inicial * 100.0

        if var_pct <= -perc_compra:
            if bot.compra_mercado:
                if indicator is None or indicator.market_signal_compra is not True:
                    print(
                        f"[ENGINE] Bot id={bot.id} condição de porcentagem_compra "
                        "atingida, mas market_signal_compra não é True ou não há "
                        "indicador. Compra ignorada."
                    )
                    return

            print(
                f"[ENGINE] Bot id={bot.id} COMPRA por porcentagem_compra! "
                f"valor_inicial={bot.valor_inicial} price_atual={price} "
                f"var_pct={var_pct:.4f}% threshold={-perc_compra}%"
            )
            simulate_buy(bot, session, settings, price)
            return

    print(
        f"[ENGINE] Bot id={bot.id} sem posição aberta; "
        f"comprar_ao_iniciar={bot.comprar_ao_iniciar}, "
        f"porcentagem_compra={bot.porcentagem_compra}, "
        f"compra_mercado={bot.compra_mercado}. "
        "Nenhuma regra de compra acionada neste ciclo."
    )


def handle_position(
    bot: Bot,
    session: Session,
    settings,
    price: float,
    indicator: Indicator | None,
) -> None:
    """
    Com posição aberta:
    - Checa STOP LOSS (independente de indicador).
    - Se não disparar stop-loss, checa TAKE PROFIT (porcentagem_venda),
      opcionalmente respeitando venda_mercado + market_signal_venda.
    """
    # 1) STOP LOSS
    stop_loss_percent = bot.stop_loss_percent or 0.0

    if stop_loss_percent > 0 and bot.valor_inicial:
        var_pct_sl = (price - bot.valor_inicial) / bot.valor_inicial * 100.0

        # stop_loss_percent é positivo (20 = -20%)
        if var_pct_sl <= -stop_loss_percent:
            print(
                f"[ENGINE] Bot id={bot.id} STOP LOSS disparado! "
                f"valor_inicial={bot.valor_inicial} price_atual={price} "
                f"var_pct={var_pct_sl:.4f}% threshold={-stop_loss_percent}%"
            )

            if bot.vender_stop_loss:
                simulate_sell(
                    bot,
                    session,
                    settings,
                    price,
                    reason="stop_loss_triggered",
                )
            else:
                print(
                    f"[ENGINE] Bot id={bot.id} com stop_loss disparado, "
                    "mas vender_stop_loss = False; mantendo posição aberta."
                )
            return

    # 2) TAKE PROFIT (porcentagem_venda)
    take_profit = bot.porcentagem_venda or 0.0
    if take_profit > 0 and bot.valor_inicial:
        base_price = bot.last_buy_price or bot.valor_inicial
        var_pct_tp = (price - base_price) / base_price * 100.0

        if var_pct_tp >= take_profit:
            if bot.venda_mercado:
                if indicator is None or indicator.market_signal_venda is not True:
                    print(
                        f"[ENGINE] Bot id={bot.id} TAKE PROFIT preço atingido, "
                        "mas market_signal_venda não é True ou não há indicador. "
                        "Venda ignorada."
                    )
                    return

            print(
                f"[ENGINE] Bot id={bot.id} TAKE PROFIT disparado! "
                f"base_price={base_price} price_atual={price} "
                f"var_pct={var_pct_tp:.4f}% threshold={take_profit}%"
            )
            simulate_sell(
                bot,
                session,
                settings,
                price,
                reason="take_profit",
            )
            return

    print(
        f"[ENGINE] Bot id={bot.id} com posição aberta; "
        "nenhuma regra de venda acionada neste ciclo."
    )


def simulate_buy(bot: Bot, session: Session, settings, price: float) -> None:
    """
    COMPRA simulada:
    - Checa saldo virtual (saldo_usdt_livre vs valor_de_trade_usdt).
    - Atualiza posição e saldo virtual.
    - Registra Trade BUY.
    """
    if bot.saldo_usdt_livre < bot.valor_de_trade_usdt:
        print(
            f"[ENGINE] Bot id={bot.id} sem saldo virtual suficiente para comprar. "
            f"saldo_livre={bot.saldo_usdt_livre}, trade={bot.valor_de_trade_usdt}"
        )
        return

    valor_trade = bot.valor_de_trade_usdt
    if price <= 0:
        print(f"[ENGINE] Preço inválido ({price}) para {bot.symbol}. Abortando compra.")
        return

    qty = valor_trade / price

    bot.has_open_position = True
    bot.qty_moeda += qty
    bot.saldo_usdt_livre -= valor_trade
    bot.last_buy_price = price
    bot.valor_inicial = price

    trade = Trade(
        bot_id=bot.id,
        symbol=bot.symbol,
        side="BUY",
        price=price,
        qty=qty,
        quote_qty=valor_trade,
        is_simulated=(settings.app_mode == "simulation"),
        fee_amount=None,
        fee_asset=None,
        realized_pnl=None,
        info="Simulated BUY executed by engine",
    )

    session.add(bot)
    session.add(trade)
    session.commit()
    session.refresh(bot)

    print(
        f"[ENGINE] Bot id={bot.id} COMPRA SIMULADA executada: "
        f"price={price}, qty={qty}, valor={valor_trade}, "
        f"saldo_livre_restante={bot.saldo_usdt_livre}"
    )


def simulate_sell(
    bot: Bot,
    session: Session,
    settings,
    price: float,
    reason: str | None = None,
) -> None:
    """
    VENDA simulada de toda a posição:
    - Atualiza saldo virtual.
    - Calcula P/L realizado.
    - Se for stop-loss, bloqueia e desliga o bot.
    """
    if not bot.has_open_position or bot.qty_moeda <= 0:
        print(
            f"[ENGINE] Bot id={bot.id} chamado para SELL mas sem posição aberta "
            f"(has_open_position={bot.has_open_position}, qty_moeda={bot.qty_moeda})."
        )
        return

    qty = bot.qty_moeda
    if price <= 0:
        print(f"[ENGINE] Preço inválido ({price}) para {bot.symbol}. Abortando venda.")
        return

    quote_value = qty * price

    base_price = bot.last_buy_price or bot.valor_inicial or price
    cost = qty * base_price
    realized_pnl = quote_value - cost

    bot.has_open_position = False
    bot.qty_moeda = 0.0
    bot.saldo_usdt_livre += quote_value
    bot.last_sell_price = price
    bot.valor_inicial = price  # novo ciclo começa aqui

    if reason == "stop_loss_triggered":
        bot.blocked = True
        bot.status = "offline"

    info_msg = "Simulated SELL executed by engine"
    if reason == "stop_loss_triggered":
        info_msg += " (stop_loss_triggered)"
    elif reason == "take_profit":
        info_msg += " (take_profit)"
    elif reason == "manual_close":
        info_msg += " (manual_close)"

    trade = Trade(
        bot_id=bot.id,
        symbol=bot.symbol,
        side="SELL",
        price=price,
        qty=qty,
        quote_qty=quote_value,
        is_simulated=(settings.app_mode == "simulation"),
        fee_amount=None,
        fee_asset=None,
        realized_pnl=realized_pnl,
        info=info_msg,
    )

    session.add(bot)
    session.add(trade)
    session.commit()
    session.refresh(bot)

    print(
        f"[ENGINE] Bot id={bot.id} VENDA SIMULADA executada: "
        f"reason={reason}, price={price}, qty={qty}, valor={quote_value}, "
        f"realized_pnl={realized_pnl}, saldo_livre={bot.saldo_usdt_livre}, "
        f"blocked={bot.blocked}, status={bot.status}"
    )
