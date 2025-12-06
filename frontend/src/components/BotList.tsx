import React, { useEffect, useState } from 'react'
import { listBots, setBotStatus, runBotCycle, blockAllBots, unblockAllBots } from '../api/client'
import type { Bot } from '../api/client'

type Props = {
  onSelectBot: (botId: number) => void
  reloadToken?: number
}

export const BotList: React.FC<Props> = ({ onSelectBot, reloadToken }) => {
  const [bots, setBots] = useState<Bot[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    try {
      setError(null)
      setLoading(true)
      const data = await listBots()
      setBots(data)
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar bots')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  useEffect(() => {
    if (reloadToken !== undefined) {
      load()
    }
  }, [reloadToken])

  const handleToggleStatus = async (bot: Bot) => {
    const newStatus = bot.status === 'online' ? 'offline' : 'online'
    try {
      const updated = await setBotStatus(bot.id, newStatus)
      setBots(prev => prev.map(b => (b.id === bot.id ? updated : b)))
    } catch (err: any) {
      alert(err.message || 'Erro ao atualizar status do bot')
    }
  }

  const handleRunCycle = async (bot: Bot) => {
    try {
      await runBotCycle(bot.id)
      alert(`Ciclo executado para o bot ${bot.name}`)
    } catch (err: any) {
      alert(err.message || 'Erro ao executar ciclo do bot')
    }
  }

  const handleBlockAll = async () => {
    try {
      const res = await blockAllBots()
      alert(`Bots bloqueados: ${res.blocked}`)
      await load()
    } catch (err: any) {
      alert(err.message || 'Erro ao bloquear todos os bots')
    }
  }

  const handleUnblockAll = async () => {
    try {
      const res = await unblockAllBots()
      alert(`Bots desbloqueados: ${res.unblocked}`)
      await load()
    } catch (err: any) {
      alert(err.message || 'Erro ao desbloquear todos os bots')
    }
  }

  return (
    <div className="bot-list">
      <div className="bot-list-header">
        <h2>Bots</h2>
        <div className="bot-list-actions">
          <button onClick={load} disabled={loading}>
            Atualizar
          </button>
          <button onClick={handleBlockAll}>
            Bloquear todos
          </button>
          <button onClick={handleUnblockAll}>
            Desbloquear todos
          </button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {bots.length === 0 && !loading && <div>Nenhum bot cadastrado ainda.</div>}

      <ul>
        {bots.map(bot => (
          <li key={bot.id} className="bot-item">
            <div className="bot-main">
              <strong>{bot.name}</strong>
              <span className={`status-${bot.status}`}>{bot.status.toUpperCase()}</span>
            </div>
            <div className="bot-meta">
              <span>Limite: {bot.saldo_usdt_limit.toFixed(2)} USDT</span>
              <span>Saldo livre: {bot.saldo_usdt_livre.toFixed(2)} USDT</span>
            </div>
            <div className="bot-actions">
              <button onClick={() => onSelectBot(bot.id)}>Ver detalhes</button>
              <button onClick={() => handleToggleStatus(bot)}>
                {bot.status === 'online' ? 'Desligar' : 'Ligar'}
              </button>
              <button onClick={() => handleRunCycle(bot)}>Rodar ciclo</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
