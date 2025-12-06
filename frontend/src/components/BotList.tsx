import React, { useEffect, useState } from 'react'
import { listBots, setBotStatus, runBotCycle } from '../api/client'
import type { Bot } from '../api/client'


type Props = {
  onSelectBot: (botId: number) => void
}

export const BotList: React.FC<Props> = ({ onSelectBot }) => {
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

  return (
    <div className="bot-list">
      <div className="bot-list-header">
        <h2>Bots</h2>
        <button onClick={load} disabled={loading}>
          Atualizar
        </button>
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
