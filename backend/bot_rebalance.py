# ==== BLOCK: BOT_REBALANCE_IMPORTS - START ====
from datetime import datetime
from typing import List

from sqlmodel import Session, select

from .db import get_session
from .models import Bot, BotAsset
from .binance_client import get_symbol_price_usdt
from .bot_risk import calculate_bot_equity_usdt
# ==== BLOCK: BOT_REBALANCE_IMPORTS - END ====


# ==== BLOCK: BOT_REBALANCE_RESULT_MODEL - START ====
class RebalancedAsset:
    def __init__(
        self,
        symbol: str,
        old_reserved: float,
        new_reserved: float,
        old_value_usdt: float,
        new_value_usdt: float,
    ):
        self.symbol = symbol
        self.old_reserved = old_reserved
        self.new_reserved = new_reserved
        self.old_value_usdt = old_value_usdt
        self.new_value_usdt = new_value_usdt


class RebalanceResult:
    def __init__(
        self,
        bot_id: int,
        bot_name: str,
        target_per_asset_usdt: float,
        total_value_before: float,
        total_value_after: float,
        insufficient_funds: bool,
        assets: List[RebalancedAsset],
    ):
        self.bot_id = bot_id
        self.bot_name = bot_name
        self.target_per_asset_usdt = target_per_asset_usdt
        self.total_value_before = total_value_before
        self.total_value_after = total_value_after
        self.insufficient_funds = insufficient_funds
        self.assets = assets
# ==== BLOCK: BOT_REBALANCE_RESULT_MODEL - END ====


# ==== BLOCK: BOT_REBALANCE_MAIN - START ====
def rebalance_bot(bot_id: int, target_per_asset_usdt: float = 10.0) -> RebalanceResult:
    """
    Rebalanceia o bot para tentar manter ~target_per_asset_usdt em cada moeda.

    Regras:
    - Primeiro, "devolve" excedente:
      - se uma moeda tiver mais que target USDT, reduz reserved_amount até o alvo
      - o excedente volta para current_balance_usdt do bot
    - Depois, tenta completar as moedas que estiverem abaixo do alvo:
      - usa primeiro o current_balance_usdt do bot
      - se não houver saldo suficiente, compra só o que der
      - marca insufficient_funds = True se alguma moeda ficar abaixo do alvo

    Tudo é feito dentro do "mundo do bot":
    - Só mexemos em reserved_amount das moedas e no current_balance_usdt do bot.
    - Preços são obtidos da Binance apenas para cálculo (USDT de referência).
    """
    with get_session() as session:
        bot = session.get(Bot, bot_id)
        if not bot:
            raise ValueError("Bot não encontrado.")

        stmt_assets = select(BotAsset).where(BotAsset.bot_id == bot_id)
        assets: list[BotAsset] = session.exec(stmt_assets).all()
        if not assets:
            raise ValueError("Nenhuma moeda configurada para este bot.")

        now = datetime.utcnow()

        # Valor total antes do rebalance
        total_before = calculate_bot_equity_usdt(bot, session)

        # Vamos trabalhar com available_usdt como "saldo interno" do rebalance
        available_usdt = bot.current_balance_usdt or 0.0

        changed_assets: list[RebalancedAsset] = []

        # Primeiro passo: devolver excedente (acima de target_per_asset_usdt)
        for asset in assets:
            price = asset.initial_price_usdt or 0.0
            if price <= 0:
                price = get_symbol_price_usdt(asset.symbol) or 0.0
                if price <= 0:
                    # Não conseguimos precificar essa moeda agora, ignora
                    continue
                asset.initial_price_usdt = price

            old_reserved = asset.reserved_amount or 0.0
            old_value = old_reserved * price

            if old_value > target_per_asset_usdt:
                # Quanto está excedendo o alvo?
                excess_value = old_value - target_per_asset_usdt
                delta_units = excess_value / price

                new_reserved = max(0.0, old_reserved - delta_units)
                new_value = new_reserved * price

                # Atualiza asset e saldo do bot
                asset.reserved_amount = new_reserved
                asset.updated_at = now
                bot.current_balance_usdt += excess_value
                available_usdt += excess_value

                changed_assets.append(
                    RebalancedAsset(
                        symbol=asset.symbol,
                        old_reserved=old_reserved,
                        new_reserved=new_reserved,
                        old_value_usdt=old_value,
                        new_value_usdt=new_value,
                    )
                )

        # Segundo passo: completar as moedas que têm menos que target_per_asset_usdt
        insufficient = False

        for asset in assets:
            price = asset.initial_price_usdt or 0.0
            if price <= 0:
                price = get_symbol_price_usdt(asset.symbol) or 0.0
                if price <= 0:
                    continue
                asset.initial_price_usdt = price

            old_reserved = asset.reserved_amount or 0.0
            old_value = old_reserved * price

            if old_value >= target_per_asset_usdt:
                # Já está no alvo ou acima (já tratamos excedente antes)
                continue

            # Quanto falta para chegar em target?
            missing_value = target_per_asset_usdt - old_value
            if missing_value <= 0:
                continue

            # Vamos usar o que tiver disponível em USDT
            allocation = min(missing_value, available_usdt)
            if allocation <= 0:
                insufficient = True
                continue

            delta_units = allocation / price
            new_reserved = old_reserved + delta_units
            new_value = new_reserved * price

            asset.reserved_amount = new_reserved
            asset.updated_at = now

            bot.current_balance_usdt -= allocation
            available_usdt -= allocation

            if allocation < missing_value:
                # Não conseguimos completar até o alvo para esta moeda
                insufficient = True

            changed_assets.append(
                RebalancedAsset(
                    symbol=asset.symbol,
                    old_reserved=old_reserved,
                    new_reserved=new_reserved,
                    old_value_usdt=old_value,
                    new_value_usdt=new_value,
                )
            )

        # Atualiza flags de rebalance no bot
        bot.last_rebalance_at = now
        bot.last_rebalance_insufficient = insufficient
        bot.updated_at = now

        session.add(bot)
        for asset in assets:
            session.add(asset)

        session.commit()

        total_after = calculate_bot_equity_usdt(bot, session)

        return RebalanceResult(
            bot_id=bot.id,
            bot_name=bot.name,
            target_per_asset_usdt=target_per_asset_usdt,
            total_value_before=total_before,
            total_value_after=total_after,
            insufficient_funds=insufficient,
            assets=changed_assets,
        )
# ==== BLOCK: BOT_REBALANCE_MAIN - END ====
