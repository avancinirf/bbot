from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from app.db.session import engine
from app.models.bot import Bot
from app.models.trade import Trade
from app.models.indicator import Indicator

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/ping")
def ping_analysis():
  return {"message": "analysis endpoint ok"}


def _get_latest_indicator(session: Session, symbol: str) -> Optional[Indicator]:
  symbol = symbol.upper()
  return (
    session.exec(
      select(Indicator)
      .where(
        Indicator.symbol == symbol,
        Indicator.interval == "5m",
      )
      .order_by(Indicator.close_time.desc())
    )
    .first()
  )


@router.get("/bot/{bot_id}")
def analyze_bot(bot_id: int):
  """
  Faz uma análise simples de um bot:
  - dados básicos do bot
  - estatísticas de trades
  - último indicador técnico
  - recomendação textual baseada em regras simples
  """
  with Session(engine) as session:
    bot = session.get(Bot, bot_id)
    if not bot:
      raise HTTPException(status_code=404, detail=f"Bot id={bot_id} não encontrado.")

    trades = list(
      session.exec(
        select(Trade)
        .where(Trade.bot_id == bot_id)
        .order_by(Trade.created_at)
      )
    )

    # Estatísticas de trades
    num_trades = len(trades)
    num_buys = sum(1 for t in trades if t.side == "BUY")
    num_sells = sum(1 for t in trades if t.side == "SELL")
    realized_pnl = sum((t.realized_pnl or 0) for t in trades)
    total_fees_usdt = sum(
      (t.fee_amount or 0) for t in trades if (t.fee_asset or "").upper() == "USDT"
    )
    last_trade_at = trades[-1].created_at if trades else None

    # Indicador mais recente
    indicator = _get_latest_indicator(session, bot.symbol)

    # Cálculo de P/L não realizado (aproximado)
    unrealized_pnl = None
    current_position_value = None
    if bot.has_open_position and bot.qty_moeda and indicator and indicator.close:
      current_position_value = float(bot.qty_moeda) * float(indicator.close)
      if bot.last_buy_price:
        custo = float(bot.qty_moeda) * float(bot.last_buy_price)
        unrealized_pnl = current_position_value - custo

    # Construir recomendação simples (regra de bolso, NÃO é conselho financeiro)
    recomendacao = "neutro"
    motivos = []

    # Situação da posição
    if bot.has_open_position:
      motivos.append("Bot está com posição aberta.")
    else:
      motivos.append("Bot está sem posição aberta.")

    # Considerar stop loss configurado
    if bot.stop_loss_percent is not None:
      motivos.append(
        f"Stop loss configurado em {bot.stop_loss_percent:.2f}% "
        f"(vender_stop_loss={bot.vender_stop_loss})."
      )

    # Considerar performance histórica
    if realized_pnl > 0:
      motivos.append(
        f"P/L realizado positivo em histórico: {realized_pnl:.6f} USDT."
      )
    elif realized_pnl < 0:
      motivos.append(
        f"P/L realizado negativo em histórico: {realized_pnl:.6f} USDT."
      )

    # Considerar indicadores
    if indicator:
      if indicator.market_signal_compra and not indicator.market_signal_venda:
        motivos.append("Indicadores marcam sinal de COMPRA.")
      elif indicator.market_signal_venda and not indicator.market_signal_compra:
        motivos.append("Indicadores marcam sinal de VENDA.")
      elif indicator.market_signal_compra and indicator.market_signal_venda:
        motivos.append(
          "Indicadores mostram sinais mistos (COMPRA e VENDA ao mesmo tempo)."
        )

      if indicator.rsi14 is not None:
        motivos.append(f"RSI14 atual: {indicator.rsi14:.2f}.")
    else:
      motivos.append("Ainda não há indicadores calculados para este símbolo.")

    # Regras simples para recomendação
    if bot.has_open_position and indicator:
      # posição aberta
      if indicator.market_signal_venda and realized_pnl > 0:
        recomendacao = "avaliar_venda_lucro"
        motivos.append(
          "Bot está em lucro realizado e há sinal de VENDA: avaliar realizar parte ou total da posição."
        )
      elif indicator.market_signal_venda and unrealized_pnl and unrealized_pnl > 0:
        recomendacao = "proteger_lucro"
        motivos.append(
          "P/L não realizado positivo com sinal de VENDA: considerar reduzir posição ou apertar stop."
        )
      elif indicator.market_signal_compra and (unrealized_pnl is not None and unrealized_pnl < 0):
        recomendacao = "manter_mas_monitorar"
        motivos.append(
          "P/L não realizado negativo, mas com sinal de COMPRA: manter posição porém monitorar risco."
        )
      else:
        recomendacao = "manter_em_observacao"
        motivos.append(
          "Sem sinal forte de compra/venda: manter em observação."
        )
    else:
      # sem posição aberta
      if indicator and indicator.market_signal_compra:
        recomendacao = "avaliar_entrada"
        motivos.append(
          "Sem posição aberta e indicadores em COMPRA: avaliar possível entrada conforme estratégia."
        )
      elif indicator and indicator.market_signal_venda:
        recomendacao = "evitar_entrada"
        motivos.append(
          "Indicadores em VENDA e bot sem posição: evitar novas entradas por enquanto."
        )
      else:
        recomendacao = "neutro"
        motivos.append(
          "Sem posição e sem sinal claro nos indicadores: aguardar melhor configuração de mercado."
        )

    return {
      "bot": {
        "id": bot.id,
        "name": bot.name,
        "symbol": bot.symbol,
        "status": bot.status,
        "blocked": bot.blocked,
        "saldo_usdt_limit": bot.saldo_usdt_limit,
        "saldo_usdt_livre": bot.saldo_usdt_livre,
        "has_open_position": bot.has_open_position,
        "qty_moeda": bot.qty_moeda,
        "last_buy_price": bot.last_buy_price,
        "last_sell_price": bot.last_sell_price,
        "valor_inicial": bot.valor_inicial,
        "stop_loss_percent": bot.stop_loss_percent,
        "vender_stop_loss": bot.vender_stop_loss,
        "porcentagem_compra": bot.porcentagem_compra,
        "porcentagem_venda": bot.porcentagem_venda,
      },
      "trades_stats": {
        "num_trades": num_trades,
        "num_buys": num_buys,
        "num_sells": num_sells,
        "realized_pnl": realized_pnl,
        "total_fees_usdt": total_fees_usdt,
        "last_trade_at": last_trade_at,
      },
      "indicator": indicator,
      "position": {
        "current_position_value": current_position_value,
        "unrealized_pnl": unrealized_pnl,
      },
      "analysis": {
        "recomendacao": recomendacao,
        "motivos": motivos,
      },
    }
