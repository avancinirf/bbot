# ==== BLOCK: BOT_INIT_IMPORTS - START ====
from datetime import datetime

from sqlmodel import Session, select

from .db import get_session
from .models import Bot, BotAsset
from .binance_client import get_symbol_price_usdt
# ==== BLOCK: BOT_INIT_IMPORTS - END ====


# ==== BLOCK: BOT_INIT_BALANCES - START ====
def initialize_bot_balances(bot_id: int) -> None:
    """
    Inicializa/recalcula os saldos LÓGICOS do bot (reserved_amount) usando
    APENAS o saldo em USDT do próprio bot (current_balance_usdt).

    Regras:
    - Cada moeda do bot tenta ter até ~10 USDT alocados.
    - Usamos o preço atual em USDT para calcular quantas unidades isso representa.
    - Se o bot não tiver USDT suficiente, alocamos o que der (pode ser < 10 USDT).
    - NÃO olhamos saldo real na Binance. O conceito aqui é 100% interno ao bot.
    """
    with get_session() as session:
        bot: Bot | None = session.get(Bot, bot_id)
        if not bot:
            return

        # Valor alvo por moeda (por enquanto fixo em 10 USDT)
        TARGET_PER_ASSET_USDT = 10.0

        # USDT disponível para alocação lógica
        available_usdt = bot.current_balance_usdt or 0.0
        if available_usdt <= 0:
            return

        # Carrega as moedas do bot
        stmt_assets = select(BotAsset).where(BotAsset.bot_id == bot_id)
        assets: list[BotAsset] = session.exec(stmt_assets).all()
        if not assets:
            return

        now = datetime.utcnow()

        for asset in assets:
            if available_usdt <= 0:
                break

            # Se já tem algum saldo reservado, por enquanto não realocamos aqui.
            # (No futuro, o rebalanceamento vai cuidar disso.)
            if asset.reserved_amount and asset.reserved_amount > 0:
                continue

            # Garante que temos um preço inicial válido
            price = asset.initial_price_usdt or 0.0
            if price <= 0:
                price = get_symbol_price_usdt(asset.symbol) or 0.0
                if price <= 0:
                    continue  # não conseguimos precificar essa moeda agora
                asset.initial_price_usdt = price

            # Quanto USDT ainda cabe nessa moeda (alvo é 10 USDT)
            # Como ela está zerada, queremos alocar até 10 USDT (ou o que tiver disponível).
            allocation_usdt = min(TARGET_PER_ASSET_USDT, available_usdt)
            if allocation_usdt <= 0:
                continue

            units = allocation_usdt / price

            # Atualiza saldo lógico dessa moeda
            asset.reserved_amount = (asset.reserved_amount or 0.0) + units
            asset.updated_at = now
            session.add(asset)

            # Debita do saldo em USDT do bot
            available_usdt -= allocation_usdt

        # Atualiza o saldo atual do bot com o que sobrou
        bot.current_balance_usdt = available_usdt
        bot.updated_at = now
        session.add(bot)

        session.commit()
# ==== BLOCK: BOT_INIT_BALANCES - END ====
