// Cliente simples de API usando fetch.
// Com o proxy do Vite, podemos usar URLs relativas tipo "/api/bots".

export type SystemState = {
  id: number
  online: boolean
  simulation_mode: boolean
  created_at: string
  updated_at: string
}

export type Bot = {
  id: number
  name: string
  status: 'online' | 'offline' | 'blocked'
  saldo_usdt_limit: number
  saldo_usdt_livre: number
  stop_loss_percent: number
  comprar_ao_iniciar: boolean
  compra_mercado: boolean
  venda_mercado: boolean
  created_at: string
  updated_at: string
}

export type IndicatorSummary = {
  open_time: string | null
  close: number | null
  ema9: number | null
  ema21: number | null
  rsi14: number | null
  macd: number | null
  macd_signal: number | null
  macd_hist: number | null
  adx: number | null
  trend_score: number | null
  trend_label: string | null
  market_signal_compra: boolean | null
  market_signal_venda: boolean | null
}

export type BotPairStatus = {
  pair_id: number
  symbol: string
  valor_de_trade_usdt: number
  valor_inicial: number | null
  porcentagem_compra: number
  porcentagem_venda: number
  has_open_position: boolean
  qty_moeda: number
  last_buy_price: number | null
  last_sell_price: number | null
  valor_atual: number | null
  var_pct_vs_valor_inicial: number | null
  unrealized_position_value_usdt: number
  unrealized_pnl_usdt: number | null
  indicator: IndicatorSummary | null
}

export type BotSummary = {
  saldo_usdt_limit: number
  saldo_usdt_livre: number
  total_position_value_usdt: number
  total_equity_usdt: number
  unrealized_pnl_usdt: number | null
}

export type BotStatusResponse = {
  bot: Bot
  summary: BotSummary
  pairs: BotPairStatus[]
}

export type Trade = {
  id: number
  bot_id: number
  bot_pair_id: number
  symbol: string
  side: 'BUY' | 'SELL'
  qty: number
  price: number
  value_usdt: number
  fee_usdt: number
  pnl_usdt: number | null
  indicator_snapshot: string | null
  rule_snapshot: string | null
  binance_order_id: string | null
  created_at: string
}

export type BotCreatePayload = {
  name: string
  saldo_usdt_limit: number
  stop_loss_percent: number
  comprar_ao_iniciar: boolean
  compra_mercado: boolean
  venda_mercado: boolean
}

async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {}),
    },
    ...options,
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API error ${res.status}: ${text}`)
  }

  return res.json() as Promise<T>
}

// -------- System --------

export function getSystemState(): Promise<SystemState> {
  return apiFetch<SystemState>('/api/system/state')
}

export function updateSystemState(body: Partial<SystemState>): Promise<SystemState> {
  return apiFetch<SystemState>('/api/system/state', {
    method: 'PUT',
    body: JSON.stringify(body),
  })
}

// -------- Bots --------

export function listBots(): Promise<Bot[]> {
  return apiFetch<Bot[]>('/api/bots')
}

export function createBot(payload: BotCreatePayload): Promise<Bot> {
  return apiFetch<Bot>('/api/bots', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getBotStatus(botId: number): Promise<BotStatusResponse> {
  return apiFetch<BotStatusResponse>(`/api/bots/${botId}/status`)
}

export function setBotStatus(botId: number, status: Bot['status']): Promise<Bot> {
  return apiFetch<Bot>(`/api/bots/${botId}/status`, {
    method: 'POST',
    body: JSON.stringify({ status }),
  })
}

export function runBotCycle(botId: number): Promise<any> {
  return apiFetch<any>(`/api/bots/${botId}/run_cycle`, {
    method: 'POST',
  })
}

export function listTrades(botId: number, limit = 20): Promise<Trade[]> {
  return apiFetch<Trade[]>(`/api/bots/${botId}/trades?limit=${limit}`)
}

export function blockAllBots(): Promise<{ blocked: number }> {
  return apiFetch<{ blocked: number }>('/api/bots/block_all', {
    method: 'POST',
  })
}

export function unblockAllBots(): Promise<{ unblocked: number }> {
  return apiFetch<{ unblocked: number }>('/api/bots/unblock_all', {
    method: 'POST',
  })
}
