import React, { useState } from 'react'
import { createBot } from '../api/client'
import type { BotCreatePayload } from '../api/client'

type Props = {
  onCreated: () => void
}

export const CreateBotForm: React.FC<Props> = ({ onCreated }) => {
  const [form, setForm] = useState<BotCreatePayload>({
    name: '',
    saldo_usdt_limit: 100,
    stop_loss_percent: -20,
    comprar_ao_iniciar: true,
    compra_mercado: true,
    venda_mercado: true,
  })

  const [loading, setLoading] = useState(false)

  const handleChange = (field: keyof BotCreatePayload, value: any) => {
    setForm(prev => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.name.trim()) {
      alert('Informe um nome para o bot.')
      return
    }
    if (form.saldo_usdt_limit <= 0) {
      alert('Saldo limite deve ser maior que zero.')
      return
    }

    try {
      setLoading(true)
      await createBot(form)
      alert('Bot criado com sucesso!')
      setForm(prev => ({
        ...prev,
        name: '',
      }))
      onCreated()
    } catch (err: any) {
      alert(err.message || 'Erro ao criar bot')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="create-bot-form">
      <h3>Novo bot</h3>
      <form onSubmit={handleSubmit}>
        <label className="full-row">
          Nome do bot
          <input
            type="text"
            value={form.name}
            onChange={e => handleChange('name', e.target.value)}
            placeholder="Ex.: Bot BTC Base"
          />
        </label>

        <label>
          Saldo limite (USDT)
          <input
            type="number"
            step="0.01"
            min={0}
            value={form.saldo_usdt_limit}
            onChange={e => handleChange('saldo_usdt_limit', Number(e.target.value))}
          />
        </label>

        <label>
          Stop loss (%)
          <input
            type="number"
            step="0.1"
            value={form.stop_loss_percent}
            onChange={e => handleChange('stop_loss_percent', Number(e.target.value))}
          />
        </label>

        <label>
          Comprar ao iniciar?
          <select
            value={form.comprar_ao_iniciar ? '1' : '0'}
            onChange={e => handleChange('comprar_ao_iniciar', e.target.value === '1')}
          >
            <option value="1">Sim</option>
            <option value="0">Não</option>
          </select>
        </label>

        <label>
          Usar índice de mercado para compra?
          <select
            value={form.compra_mercado ? '1' : '0'}
            onChange={e => handleChange('compra_mercado', e.target.value === '1')}
          >
            <option value="1">Sim</option>
            <option value="0">Não</option>
          </select>
        </label>

        <label>
          Usar índice de mercado para venda?
          <select
            value={form.venda_mercado ? '1' : '0'}
            onChange={e => handleChange('venda_mercado', e.target.value === '1')}
          >
            <option value="1">Sim</option>
            <option value="0">Não</option>
          </select>
        </label>

        <div className="full-row">
          <button type="submit" disabled={loading}>
            {loading ? 'Criando...' : 'Criar bot'}
          </button>
        </div>
      </form>
    </div>
  )
}
