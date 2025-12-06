import React, { useEffect, useState } from 'react'
import { getSystemState, updateSystemState } from '../api/client'
import type { SystemState } from '../api/client'


export const SystemBar: React.FC = () => {
  const [state, setState] = useState<SystemState | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    try {
      setError(null)
      const data = await getSystemState()
      setState(data)
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar estado do sistema')
    }
  }

  useEffect(() => {
    load()
  }, [])

  const toggleOnline = async () => {
    if (!state) return
    try {
      setLoading(true)
      const updated = await updateSystemState({ online: !state.online })
      setState(updated)
    } catch (err: any) {
      setError(err.message || 'Erro ao atualizar estado')
    } finally {
      setLoading(false)
    }
  }

  const toggleSimulation = async () => {
    if (!state) return
    try {
      setLoading(true)
      const updated = await updateSystemState({ simulation_mode: !state.simulation_mode })
      setState(updated)
    } catch (err: any) {
      setError(err.message || 'Erro ao atualizar modo simulado')
    } finally {
      setLoading(false)
    }
  }

  if (!state) {
    return (
      <div className="system-bar">
        <span>Carregando estado do sistema...</span>
        {error && <span className="error">{error}</span>}
      </div>
    )
  }

  return (
    <div className="system-bar">
      <div>
        <strong>Sistema:</strong>{' '}
        <span className={state.online ? 'status-online' : 'status-offline'}>
          {state.online ? 'ONLINE' : 'OFFLINE'}
        </span>
        <button onClick={toggleOnline} disabled={loading}>
          {state.online ? 'Desligar' : 'Ligar'}
        </button>
      </div>

      <div>
        <strong>Modo:</strong>{' '}
        <span className={state.simulation_mode ? 'mode-sim' : 'mode-real'}>
          {state.simulation_mode ? 'Simulado' : 'Real'}
        </span>
        <button onClick={toggleSimulation} disabled={loading}>
          Alternar modo
        </button>
      </div>

      {error && <div className="error">{error}</div>}
    </div>
  )
}
