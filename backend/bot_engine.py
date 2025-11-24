# ==== BLOCK: BOT_ENGINE_IMPORTS - START ====
import asyncio
import os
from datetime import datetime, timedelta

from sqlmodel import select

from .db import get_session
from .models import Bot, BotAsset
from .routes_bot_simtrade import simulate_trade
from .routes_bot_trade import _execute_spot_market_swap_via_usdt
from .bot_risk import check_and_handle_stop_loss
from .bot_rebalance import rebalance_bot
# ==== BLOCK: BOT_ENGINE_IMPORTS - END ====


# ==== BLOCK: BOT_ENGINE_CONFIG - START ====
ENGINE_INTERVAL_SECONDS = int(os.getenv("BOT_ENGINE_INTERVAL_SECONDS", "15"))
REBALANCE_INTERVAL_SECONDS = int(os.getenv("BOT_REBALANCE_INTERVAL_SECONDS", "3600"))
# ==== BLOCK: BOT_ENGINE_CONFIG - END ====


# ==== BLOCK: TRADE_OPPORTUNITY_HELPER - START ====
def find_opportunity_for_bot(bot: Bot, assets: list[BotAsset]):
    """
    Função simples que procura oportunidade:
    - Uma moeda marcada para SELL com preço acima do threshold
    - Uma moeda marcada para BUY com preço abaixo do threshold
    Esta função é temporária até termos o módulo completo consolidado.
    """
    opp_sell = None
    opp_buy = None

    for a in assets:
        if a.can_sell:
            if a.initial_price_usdt > 0:
                current = a.initial_price_usdt  # placeholder real em breve
        # (Nota: será substituído pelo módulo final de análise.)
    # Esta função será substituída – por agora deixamos dummy
    return None
# ==== BLOCK: TRADE_OPPORTUNITY_HELPER - END ====


# ==== BLOCK: BOT_ENGINE_EXECUTOR - START ====
def _process_bot_trade(bot: Bot, session):
    """
    Executa um trade conforme o trade_mode do bot.
    Modo SIMULATED -> simulate_trade()
    Modo REAL      -> _execute_spot_market_swap_via_usdt()
    """

    # 1) Carrega assets
    stmt = select(BotAsset).where(BotAsset.bot_id == bot.id)
    assets = session.exec(stmt).all()
    if not assets:
        return "Bot sem assets configurados."

    # 2) Obtém oportunidade (placeholder por enquanto)
    # Vamos usar a lógica já existente no seu módulo routes_bot_simtrade
    opp = simulate_trade(bot.id, session=session, only_detect=True)
    if not opp or not opp.sell_symbol or not opp.buy_symbol:
        return "Nenhuma oportunidade encontrada."

    sell_symbol = opp.sell_symbol
    buy_symbol = opp.buy_symbol

    # 3) Seleciona os assets correspondentes
    sell_asset = next((a for a in assets if a.symbol == sell_symbol), None)
    buy_asset = next((a for a in assets if a.symbol == buy_symbol), None)

    if not sell_asset or not buy_asset:
        return "Par inválido dentro do bot."

    if sell_asset.is_locked or buy_asset.is_locked:
        return "Par bloqueado aguardando trade anterior."

    # Lock
    sell_asset.is_locked = True
    buy_asset.is_locked = True
    session.add(sell_asset)
    session.add(buy_asset)
    session.commit()

    try:
        if bot.trade_mode == "REAL":
            result = _execute_spot_market_swap_via_usdt(
                bot=bot,
                sell_asset=sell_asset,
                buy_asset=buy_asset,
                trade_unit_usdt=10.0,
                session=session,
            )
        else:
            result = simulate_trade(
                bot.id,
                session=session,
                forced_pair=(sell_symbol, buy_symbol)
            )

        return result.message

    finally:
        sell_asset.is_locked = False
        buy_asset.is_locked = False
        session.add(sell_asset)
        session.add(buy_asset)
        session.commit()
# ==== BLOCK: BOT_ENGINE_EXECUTOR - END ====


# ==== BLOCK: BOT_ENGINE_CYCLE - START ====
def run_bot_cycle() -> None:
    """
    Executa UM ciclo simples do bot:
    - procura um bot ativo
    - verifica stop-loss
    - executa trade REAL ou SIMULATED conforme config
    - executa rebalance se estiver no intervalo
    """
    with get_session() as session:
        stmt = select(Bot).where(Bot.is_active == True)
        active_bots = session.exec(stmt).all()
        if not active_bots:
            return

        bot = active_bots[0]

        # 1) STOP LOSS
        stop_triggered, current_value, loss_percent = check_and_handle_stop_loss(
            bot, session
        )
        if stop_triggered:
            print(f"[BOT_ENGINE] Stop-loss acionado para {bot.name}.")
            return

        # 2) TRADE executado conforme MODO
        trade_msg = _process_bot_trade(bot, session)
        if trade_msg:
            print(f"[BOT_ENGINE] {trade_msg}")

        # 3) REBALANCE
        now = datetime.utcnow()
        last = bot.last_rebalance_at

        should_rebalance = (
            last is None or (now - last).total_seconds() >= REBALANCE_INTERVAL_SECONDS
        )

        if should_rebalance:
            try:
                result = rebalance_bot(bot_id=bot.id, target_per_asset_usdt=10.0)
                status = "INSUFICIENTE" if result.insufficient_funds else "OK"
                print(
                    f"[BOT_ENGINE] Rebalance automático do bot {bot.id} "
                    f"({bot.name}) concluído. Status: {status}"
                )
            except Exception as e:
                print(f"[BOT_ENGINE] Erro ao rebalancear bot {bot.id}: {e}")
# ==== BLOCK: BOT_ENGINE_CYCLE - END ====


# ==== BLOCK: BOT_ENGINE_LOOP - START ====
async def start_bot_engine() -> None:
    await asyncio.sleep(5)
    while True:
        try:
            run_bot_cycle()
        except Exception as e:
            print(f"[BOT_ENGINE] Erro no ciclo: {e}")
        await asyncio.sleep(ENGINE_INTERVAL_SECONDS)
# ==== BLOCK: BOT_ENGINE_LOOP - END ====
