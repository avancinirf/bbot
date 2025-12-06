import React, { useEffect, useState } from 'react'
import { getBotStatus } from '../api/client'
import type { BotStatusResponse } from '../api/client'


type Props = {
  botId: number | null
}

export const BotDetails: React.FC<Props> = ({ botId }) => {
  const [data, setData] = useState<BotStatusResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      if (!botId) {
        setData(null)
        return
      }
      try {
        setError(null)
        setLoading(true)
        const resp = await getBotStatus(botId)
        setData(resp)
      } catch (err: any) {
        setError(err.message || 'Erro ao carregar status do bot')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [botId])

  if (!botId) {
    return <div className="bot-details">Selecione um bot para ver os detalhes.</div>
  }

  if (loading) {
    return <div className="bot-details">Carregando detalhes do bot...</div>
  }

  if (error) {
    return <div className="bot-details error">{error}</div>
  }

  if (!data) {
    return <div className="bot-details">Sem dados.</div>
  }

  const { bot, summary, pairs } = data

  return (
    <div className="bot-details">
      <h2>Bot: {bot.name}</h2>
      <div className="bot-details-summary">
        <div>
          <strong>Status:</strong> <span className={`status-${bot.status}`}>{bot.status.toUpperCase()}</span>
        </div>
        <div>
          <strong>Saldo limite:</strong> {summary.saldo_usdt_limit.toFixed(2)} USDT
        </div>
        <div>
          <strong>Saldo livre:</strong> {summary.saldo_usdt_livre.toFixed(2)} USDT
        </div>
        <div>
          <strong>Posições:</strong> {summary.total_position_value_usdt.toFixed(2)} USDT
        </div>
        <div>
          <strong>Equity total:</strong> {summary.total_equity_usdt.toFixed(2)} USDT
        </div>
        <div>
          <strong>PnL não realizado:</strong>{' '}
          {summary.unrealized_pnl_usdt !== null
            ? summary.unrealized_pnl_usdt.toFixed(4) + ' USDT'
            : 'N/A'}
        </div>
      </div>

      <h3>Moedas do bot</h3>
      {pairs.length === 0 && <div>Este bot não tem pares configurados.</div>}

      {pairs.length > 0 && (
        <table className="pairs-table">
          <thead>
            <tr>
              <th>Par</th>
              <th>Valor trade (USDT)</th>
              <th>Valor inicial</th>
              <th>Valor atual</th>
              <th>% vs inicial</th>
              <th>Posição</th>
              <th>Valor posição (USDT)</th>
              <th>Trend</th>
              <th>RSI</th>
            </tr>
          </thead>
          <tbody>
            {pairs.map(pair => (
              <tr key={pair.pair_id}>
                <td>{pair.symbol}</td>
                <td>{pair.valor_de_trade_usdt.toFixed(2)}</td>
                <td>{pair.valor_inicial !== null ? pair.valor_inicial.toFixed(2) : '-'}</td>
                <td>{pair.valor_atual !== null ? pair.valor_atual.toFixed(2) : '-'}</td>
                <td>
                  {pair.var_pct_vs_valor_inicial !== null
                    ? pair.var_pct_vs_valor_inicial.toFixed(2) + ' %'
                    : '-'}
                </td>
                <td>
                  {pair.has_open_position
                    ? `${pair.qty_moeda.toFixed(8)} (aberta)`
                    : 'sem posição'}
                </td>
                <td>{pair.unrealized_position_value_usdt.toFixed(4)}</td>
                <td>{pair.indicator?.trend_label ?? '-'}</td>
                <td>
                  {pair.indicator?.rsi14 !== null && pair.indicator?.rsi14 !== undefined
                    ? pair.indicator.rsi14.toFixed(2)
                    : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
