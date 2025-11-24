# ==== BLOCK: ROUTES_BOT_ASSETS - START ====
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from .db import get_session
from .models import Bot, BotAsset, BotAssetCreate, BotAssetUpdate
from .binance_client import validate_symbol_exists, get_symbol_price_usdt

router = APIRouter()


# Lista todos os assets de um bot
@router.get("/api/bots/{bot_id}/assets/")
def list_bot_assets(bot_id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")

    stmt = select(BotAsset).where(BotAsset.bot_id == bot_id)
    assets = session.exec(stmt).all()
    return assets


# Cria um asset para o bot (com defaults de -5 e +5)
@router.post("/api/bots/{bot_id}/assets/")
def add_asset_to_bot(
    bot_id: int,
    asset: BotAssetCreate,
    session: Session = Depends(get_session),
):
    # Verificar se bot existe
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")

    # Não permitir adicionar moeda se o bot estiver ativo
    if bot.is_active:
        raise HTTPException(
            status_code=400,
            detail="Não é permitido adicionar moeda com o bot ativo. Desative o bot primeiro.",
        )

    # Valores default se não enviados
    buy_percent = asset.buy_percent if asset.buy_percent is not None else -5.0
    sell_percent = asset.sell_percent if asset.sell_percent is not None else 5.0

    # Regras lógicas (sem limitar range)
    if buy_percent >= 0:
        raise HTTPException(
            status_code=400,
            detail="buy_percent deve ser negativo (compra quando cair).",
        )
    if sell_percent <= 0:
        raise HTTPException(
            status_code=400,
            detail="sell_percent deve ser positivo (venda quando subir).",
        )

    # Validar símbolo na Binance
    if not validate_symbol_exists(asset.symbol):
        raise HTTPException(
            status_code=400,
            detail=f"Símbolo {asset.symbol} não existe na Binance.",
        )

    # Buscar preço inicial em USDT
    initial_price = get_symbol_price_usdt(asset.symbol)

    db_asset = BotAsset(
        bot_id=bot_id,
        symbol=asset.symbol.upper(),
        buy_percent=buy_percent,
        sell_percent=sell_percent,
        can_buy=True,
        can_sell=True,
        initial_price_usdt=initial_price,
        reserved_amount=0.0,
    )

    session.add(db_asset)
    session.commit()
    session.refresh(db_asset)
    return db_asset


# Atualiza configurações de um asset (percentuais e flags)
@router.patch("/api/bots/{bot_id}/assets/{asset_id}")
def update_bot_asset(
    bot_id: int,
    asset_id: int,
    payload: BotAssetUpdate,
    session: Session = Depends(get_session),
):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")

    # Não permitir editar moeda com bot ativo
    if bot.is_active:
        raise HTTPException(
            status_code=400,
            detail="Não é permitido editar moeda com o bot ativo. Desative o bot primeiro.",
        )

    asset = session.get(BotAsset, asset_id)
    if not asset or asset.bot_id != bot_id:
        raise HTTPException(status_code=404, detail="Asset não encontrado para este bot.")

    if payload.buy_percent is not None:
        if payload.buy_percent >= 0:
            raise HTTPException(
                status_code=400,
                detail="buy_percent deve ser negativo (compra quando cair).",
            )
        asset.buy_percent = payload.buy_percent

    if payload.sell_percent is not None:
        if payload.sell_percent <= 0:
            raise HTTPException(
                status_code=400,
                detail="sell_percent deve ser positivo (venda quando subir).",
            )
        asset.sell_percent = payload.sell_percent

    if payload.can_buy is not None:
        asset.can_buy = payload.can_buy

    if payload.can_sell is not None:
        asset.can_sell = payload.can_sell

    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset


# Remove um asset do bot
@router.delete("/api/bots/{bot_id}/assets/{asset_id}")
def delete_bot_asset(bot_id: int, asset_id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado.")

    # Não permitir remover moeda com bot ativo
    if bot.is_active:
        raise HTTPException(
            status_code=400,
            detail="Não é permitido remover moeda com o bot ativo. Desative o bot primeiro.",
        )

    asset = session.get(BotAsset, asset_id)
    if not asset or asset.bot_id != bot_id:
        raise HTTPException(status_code=404, detail="Asset não encontrado para este bot.")

    session.delete(asset)
    session.commit()
    return {"detail": "Asset removido com sucesso."}
# ==== BLOCK: ROUTES_BOT_ASSETS - END ====
