# ==== BLOCK: BOT_RISK_IMPORTS - START ====
from typing import Tuple

from sqlmodel import Session, select

from .models import Bot, BotAsset, TradeLog
from .binance_client import get_symbol_price_usdt
# ==== BLOCK: BOT_RISK_IMPORTS - END ====


# ==== BLOCK: BOT_RISK_EQUITY - START ====
def calculate_bot_equity_usdt(bot: Bot, session: Session) -> float:
    """
    Calcula o valor total atual do bot em USDT:
    - saldo atual em USDT do bot (current_balance_usdt)
    - + soma(reserved_amount_moeda * preço_atual_moeda_em_USDT)
    """
    equity = bot.current_balance_usdt or 0.0

    stmt_assets = select(BotAsset).where(BotAsset.bot_id == bot.id)
    assets = session.exec(stmt_assets).all()

    for asset in assets:
        if not asset.reserved_amount or asset.reserved_amount <= 0:
            continue

        price = get_symbol_price_usdt(asset.symbol) or asset.initial_price_usdt or 0.0
        if price <= 0:
            continue

        equity += asset.reserved_amount * price

    return equity
# ==== BLOCK: BOT_RISK_EQUITY - END ====


# ==== BLOCK: BOT_RISK_CHECK_STOP - START ====
def check_and_handle_stop_loss(bot: Bot, session: Session) -> Tuple[bool, float, float]:
    """
    Verifica se o bot atingiu o stop-loss.

    Retorna (stop_acionado, valor_atual, perda_percentual)

    Regras:
    - Se stop_loss_percent <= 0 ou saldo inicial <= 0 -> não faz nada.
    - perda_percentual = max(0, (saldo_inicial - valor_atual) / saldo_inicial * 100)
    - Se perda_percentual >= stop_loss_percent:
        - desativa o bot (is_active = False)
        - zera reserved_amount de todas as moedas do bot
        - registra um TradeLog com side = 'STOP'
    """
    if not bot.stop_loss_percent or bot.stop_loss_percent <= 0:
        return False, 0.0, 0.0

    if not bot.initial_balance_usdt or bot.initial_balance_usdt <= 0:
        return False, 0.0, 0.0

    current_value = calculate_bot_equity_usdt(bot, session)
    initial_value = bot.initial_balance_usdt

    # perda em %
    loss_percent = (initial_value - current_value) / initial_value * 100.0
    if loss_percent < 0:
        loss_percent = 0.0  # se estiver em lucro, não conta como perda

    if loss_percent < bot.stop_loss_percent:
        return False, current_value, loss_percent

    # Stop-loss acionado
    bot.is_active = False

    # Zera reserved_amount de todas as moedas (libera recursos internos do bot)
    stmt_assets = select(BotAsset).where(BotAsset.bot_id == bot.id)
    assets = session.exec(stmt_assets).all()
    for asset in assets:
        asset.reserved_amount = 0.0
        session.add(asset)

    # Registra um log indicando o stop
    msg = (
        f"STOP-LOSS acionado: perda de aproximadamente {loss_percent:.2f}% "
        f"(valor atual ~{current_value:.2f} USDT, inicial ~{initial_value:.2f} USDT)."
    )
    log = TradeLog(
        bot_id=bot.id,
        from_symbol="USDT",
        to_symbol="USDT",
        side="STOP",
        amount_from=0.0,
        amount_to=0.0,
        price_usdt=current_value,
        message=msg,
    )

    session.add(bot)
    session.add(log)
    session.commit()
    session.refresh(bot)
    session.refresh(log)

    return True, current_value, loss_percent
# ==== BLOCK: BOT_RISK_CHECK_STOP - END ====
