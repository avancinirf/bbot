import React, { useEffect, useState } from 'react'
import {
  getBotStatus,
  listTrades,
  getAvailablePairs,
  addPairToBot,
  syncMarket,
  runBotCycle,
} from '../api/client'
import type { BotStatusResponse, Trade } from '../api/client'

type Props = {
  botId: number | null
}

export const BotDetails: React.FC<Props> = ({ botId }) => {
  const [data, setData] = useState<BotStatusResponse | null>(null)
  const [trades, setTrades] = useState<Trade[]>([])
  const [loading, setLoading] = useState(false)
  const [tradesLoading, setTradesLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [tradesError, setTradesError] = useState<string | null>(null)

  const [availablePairs, setAvailablePairs] = useState<string[]>([])
  const [newPairSymbol, setNewPairSymbol] = useState<string>('')
  const [newPairTradeValue, setNewPairTradeValue] = useState<number>(10)
  const [newPairPctCompra, setNewPairPctCompra] = useState<number>(0)
  const [newPairPctVenda, setNewPairPctVenda] = useState<number>(5)
  const [pairLoading, setPairLoading] = useState(false)
  const [pairError, setPairError] = useState<string | null>(null)

  const [autoLoading, setAutoLoading] = useState(false)
  const [autoError, setAutoError] = useState<string | null>(null)

  const loadStatus = async (id: number) => {
    try {
      setError(null)
      setLoading(true)
      const resp = await getBotStatus(id)
      setData(resp)
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar status do bot')
    } finally {
      setLoading(false)
    }
  }

  const loadTrades = async (id: number) => {
    try {
      setTradesError(null)
      setTradesLoading(true)
      const resp = await listTrades(id, 20)
      setTrades(resp)
    } catch (err: any) {
      setTradesError(err.message || 'Erro ao carregar trades do bot')
    } finally {
      setTradesLoading(false)
    }
  }

  const loadAvailablePairs = async () => {
    try {
      const list = await getAvailablePairs()
      setAvailablePairs(list)
      if (!newPairSymbol && list.length > 0) {
        setNewPairSymbol(list[0])
      }
    } catch (err: any) {
      console.error('Erro ao carregar pares disponíveis', err)
    }
  }

  useEffect(() => {
    loadAvailablePairs()
  }, [])

  useEffect(() => {
    if (!botId) {
      setData(null)
      setTrades([])
      return
    }
    loadStatus(botId)
    loadTrades(botId)
  }, [botId])

  const handleAddPair = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!botId || !newPairSymbol) return

    if (newPairTradeValue <= 0) {
      setPairError('Valor de trade deve ser maior que zero.')
      return
    }

    try {
      setPairError(null)
      setPairLoading(true)
      await addPairToBot(botId, {
        symbol: newPairSymbol,
        valor_de_trade_usdt: newPairTradeValue,
        porcentagem_compra: newPairPctCompra,
        porcentagem_venda: newPairPctVenda,
      })
      await loadStatus(botId)
      alert('Par adicionado ao bot.')
    } catch (err: any) {
      setPairError(err.message || 'Erro ao adicionar par')
    } finally {
      setPairLoading(false)
    }
  }

  const handleSyncAndRun = async () => {
    if (!botId || !data) return

    const symbols = data.pairs.map(p => p.symbol)
    if (symbols.length === 0) {
      setAutoError('Este bot não tem pares para sincronizar.')
      return
    }

    try {
      setAutoError(null)
      setAutoLoading(true)

      // Sincroniza mercado para todos os símbolos do bot
      await Promise.all(symbols.map(symbol => syncMarket(symbol, 200)))

      // Executa 1 ciclo do bot
      await runBotCycle(botId)

      // Recarrega status e trades
      await loadStatus(botId)
      await loadTrades(botId)

      alert('Mercado sincronizado e ciclo executado.')
    } catch (err: any) {
      setAutoError(err.message || 'Erro ao sincronizar mercado e executar ciclo')
    } finally {
      setAutoLoading(false)
    }
  }

  if (!botId) {
    return <div className="bot-details">Selecione um bot para ver os detalhes.</div>
  }

  if (loading && !data) {
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
          <strong>Status:</strong>{' '}
          <span className={`status-${bot.status}`}>{bot.status.toUpperCase()}</span>
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

      <div className="add-pair-form">
        <h3>Adicionar par ao bot</h3>
        {pairError && <div className="error">{pairError}</div>}
        <form onSubmit={handleAddPair}>
          <label>
            Par
            <select
              value={newPairSymbol}
              onChange={e => setNewPairSymbol(e.target.value)}
            >
              <option value="">Selecione...</option>
              {availablePairs.map(p => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </label>

          <label>
            Valor trade (USDT)
            <input
              type="number"
              step="0.01"
              min={0}
              value={newPairTradeValue}
              onChange={e => setNewPairTradeValue(Number(e.target.value))}
            />
          </label>

          <label>
            % compra (≤ 0)
            <input
              type="number"
              step="0.1"
              value={newPairPctCompra}
              onChange={e => setNewPairPctCompra(Number(e.target.value))}
            />
          </label>

          <label>
            % venda (≥ 0)
            <input
              type="number"
              step="0.1"
              value={newPairPctVenda}
              onChange={e => setNewPairPctVenda(Number(e.target.value))}
            />
          </label>

          <div className="add-pair-submit">
            <button type="submit" disabled={pairLoading || !newPairSymbol}>
              {pairLoading ? 'Adicionando...' : 'Adicionar par'}
            </button>
          </div>
        </form>
      </div>

      <h3>Moedas do bot</h3>

      <div className="bot-details-actions">
        <button onClick={handleSyncAndRun} disabled={autoLoading || pairs.length === 0}>
          {autoLoading ? 'Sincronizando...' : 'Sync mercado + rodar ciclo'}
        </button>
        {autoError && <span className="error">{autoError}</span>}
      </div>

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

      <h3>Últimos trades</h3>
      <div className="trades-header">
        <button onClick={() => botId && loadTrades(botId)} disabled={tradesLoading}>
          Atualizar trades
        </button>
      </div>
      {tradesError && <div className="error">{tradesError}</div>}
      {trades.length === 0 && !tradesLoading && (
        <div>Nenhum trade registrado ainda para este bot.</div>
      )}

      {trades.length > 0 && (
        <table className="trades-table">
          <thead>
            <tr>
              <th>Data</th>
              <th>Side</th>
              <th>Par</th>
              <th>Qtd</th>
              <th>Preço</th>
              <th>Valor (USDT)</th>
              <th>PnL (USDT)</th>
              <th>Regra</th>
            </tr>
          </thead>
          <tbody>
            {trades.map(tr => (
              <tr key={tr.id}>
                <td>{new Date(tr.created_at).toLocaleString()}</td>
                <td className={tr.side === 'BUY' ? 'side-buy' : 'side-sell'}>
                  {tr.side}
                </td>
                <td>{tr.symbol}</td>
                <td>{tr.qty.toFixed(8)}</td>
                <td>{tr.price.toFixed(2)}</td>
                <td>{tr.value_usdt.toFixed(4)}</td>
                <td>{tr.pnl_usdt !== null ? tr.pnl_usdt.toFixed(4) : '-'}</td>
                <td>{tr.rule_snapshot}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
