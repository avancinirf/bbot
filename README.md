# bbot – Bot de micro trade na Binance (SPOT)

Bot de trade automatizado focado em **micro trades** em criptomoedas usando a **API da Binance** (testnet ou produção).
O sistema:
- roda inteiramente em um **container Docker**,
- usa **SQLite** para persistência de bots, moedas e logs,
- permite operar em modo **SIMULADO** ou **REAL** (market SPOT na Binance),
- nunca faz **saque ou depósito**, apenas **trades dentro da conta**.

---

## Funcionalidades principais

### Bots
- Criar vários bots, mas **apenas 1 bot pode estar ativo de cada vez**.
- Cada bot:
  - possui **saldo inicial** em USDT (virtual dentro do bot),
  - tem **saldo atual** em USDT, atualizado por trades,
  - tem **stop-loss** configurável (ex.: 40% de perda do valor do bot),
  - possui **modo de operação**:
    - `SIMULATED` – só simula trades, não envia ordens à Binance (✔ implementado).
    - `REAL_MARKET_SPOT` – envia ordens MARKET reais para Binance (✔ implementado, usando API keys).

### Ativos (moedas do bot)
- Cada bot possui uma lista de **ativos** (moedas: BTC, ETH, SOL, XRP etc.).
- Para cada ativo:
  - `symbol` (ex.: `ETH`), validado na Binance em par com USDT.
  - `initial_price_usdt`: preço de referência quando o bot foi iniciado ou após último trade.
  - `reserved_amount`: quantidade da moeda reservada para o bot (equivalente a ~10 USDT).
  - `buy_percent`: % mínima abaixo do preço inicial para **permitir compra** (ex.: -5%).
  - `sell_percent`: % mínima acima do preço inicial para **permitir venda** (ex.: +10%).
  - flags `can_buy`, `can_sell`.

### Análise de mercado
- Endpoint que lê dados da Binance (klines) para cada `symbol` do bot e calcula:
  - **preço atual em USDT**,
  - **variação (%)** vs `initial_price_usdt`,
  - **RSI(14)**,
  - **EMA rápida e lenta**,
  - **tendência** (`UP` / `DOWN`).
- Endpoint de **oportunidade de trade**:
  - separa moedas em:
    - zona de compra (abaixo do `buy_percent`) e
    - zona de venda (acima do `sell_percent`),
  - escolhe par candidato **(vender A, comprar B)** com base na melhor combinação.

### Execução de trade
- **Simulação**:
  - endpoint que simula swap entre duas moedas:
    - vende ~10 USDT da moeda A,
    - compra ~10 USDT da moeda B,
    - atualiza `reserved_amount` e `initial_price_usdt`,
    - grava log em `TradeLog` com `side="SIMULATED_SWAP"`.
- **Real (Binance SPOT MARKET)**:
  - endpoint que:
    - lê filtros da Binance (LOT_SIZE, MIN_NOTIONAL),
    - ajusta a quantidade,
    - envia:
      - ordem MARKET SELL de `sell_symbol`/USDT,
      - ordem MARKET BUY de `buy_symbol`/USDT,
    - grava log com `side="REAL_SWAP"` (nome pode variar conforme implementação).

### Risco e Stop-Loss
- Cálculo de **equity total do bot em USDT**:
  - soma do saldo USDT do bot + valor das moedas reservadas convertidas para USDT.
- Quando perda ≥ `stop_loss_percent` do valor inicial:
  - o bot entra em **modo STOP**:
    - gera `TradeLog` com `side="STOP"`,
    - desativa o bot (`is_active = false`),
    - libera moedas (lógica depende da versão atual).

### Rebalanceamento
- Rebalanceamento manual via endpoint:
  - objetivo: manter **~10 USDT por moeda** do bot.
  - calcula valor atual de cada moeda em USDT,
  - identifica excedentes e déficits,
  - usa USDT + excedentes para tentar recompor ~10 USDT/ativo.
- Marca se o último rebalance teve **saldo insuficiente** para todas as moedas.

---

## Estado atual (Implementado vs Pendente)

### Implementado (testado via `curl` e UI básica)

- [x] API `/api/health`
- [x] Criação de bot (`POST /api/bots/`)
- [x] Listar bots (`GET /api/bots/`)
- [x] Ativar/desativar bot (`PATCH /api/bots/{id}/activate`, `/deactivate`)
- [x] Definir `initial_balance_usdt`, `stop_loss_percent`, `trade_mode`
- [x] CRUD básico de assets do bot (`/api/bots/{bot_id}/assets/`)
- [x] Integração Binance: preços e klines para símbolos `XXXUSDT`
- [x] Endpoint de análise por bot (`/api/bots/{id}/analysis/`)
- [x] Endpoint de indicadores (`/api/bots/{id}/indicators/`)
- [x] Endpoint de oportunidade (`/api/bots/{id}/opportunity/`)
- [x] Simulação de trade (`/api/bots/{id}/simulate-trade/`)
- [x] Logs de trades (`/api/bots/{id}/logs/`)
- [x] Rebalance (`/api/bots/{id}/rebalance/`)
- [x] Trade real MARKET SPOT via Binance (`/api/bots/{id}/trade/market-swap/`)
- [x] Interface React simples exibindo:
  - bot ativo, saldo inicial vs atual, stop-loss
  - lista de ativos e variação
  - indicadores e oportunidade
  - logs

### Planejado / pendente (já combinado mas não totalmente pronto)

- [ ] WebSocket para atualização em tempo real de:
  - preços,
  - análise,
  - logs.
- [ ] Engine automática de execução contínua via backend:
  - loop que:
    - verifica oportunidade,
    - respeita trade_mode (SIMULATED vs REAL),
    - dispara rebalance em intervalos configurados.
- [ ] Formulário no frontend para:
  - criar bot (sem precisar `curl`),
  - adicionar/remover moedas no bot (com bot desativado),
  - editar `buy_percent` e `sell_percent` com defaults (ex.: -3%, +5%).
- [ ] Estratégias mais flexíveis (0.5%, 1%, etc.):
  - hoje já é possível, mas queremos uma UX mais clara.
- [ ] Política mais sofisticada de “excedente de moedas”:
  - excedente de moedas como “saldo extra do bot” para rebalanceamento,
  - nunca usar recursos de bots desativados.

---

## 3.2. `docs/architecture.md`

```md
# Arquitetura do bbot

## Visão geral

Arquitetura **monolítica**, com:
- backend FastAPI + engine do bot,
- frontend React (build estático via Vite),
- DB SQLite,
- tudo empacotado em **um único container Docker**.

## Backend

### Principais módulos

- `main.py`
  - Cria instância FastAPI.
  - Configura CORS.
  - Inclui routers:
    - `routes_bots`
    - `routes_bot_assets`
    - `routes_bot_analysis`
    - `routes_trade_logs`
    - `routes_bot_trade`
    - `routes_bot_simtrade`
    - `routes_bot_rebalance`
  - Inicializa DB (se necessário).

- `models.py`
  - `Bot`
    - `id`, `name`
    - `is_active`
    - `trade_mode` (`SIMULATED`, `REAL_MARKET_SPOT`)
    - `initial_balance_usdt`, `current_balance_usdt`
    - `stop_loss_percent`, `stop_behavior`
    - `last_rebalance_at`, `last_rebalance_insufficient`
    - `created_at`, `updated_at`
  - `BotAsset`
    - `id`, `bot_id`
    - `symbol`
    - `initial_price_usdt`
    - `reserved_amount`
    - `buy_percent`, `sell_percent`
    - `can_buy`, `can_sell`
    - `created_at`, `updated_at`
  - `TradeLog`
    - `id`, `bot_id`
    - `from_symbol`, `to_symbol`
    - `amount_from`, `amount_to`
    - `price_usdt`
    - `side` (`SELL`, `SIMULATED_SWAP`, `STOP`, etc.)
    - `message`
    - `created_at`

- `binance_client.py`
  - Lê configs (`BINANCE_API_KEY`, `BINANCE_API_SECRET`, `BINANCE_TESTNET`).
  - Cria client da Binance (spot).
  - Funções:
    - `get_symbol_price_usdt(symbol)`
    - `validate_symbol_usdt(symbol)` / `validate_symbol_exists`
    - `get_symbol_klines(symbol, interval, limit)`
    - `get_exchange_info()` para filtros.
    - `get_symbol_filters(symbol)` e helpers (LOT_SIZE, MIN_NOTIONAL).
    - `adjust_quantity_to_filters(symbol, qty)`
    - envio de ordens MARKET: buy / sell.

- `indicators.py`
  - Cálculo de:
    - RSI (14 períodos),
    - EMA rápida e lenta,
    - tendência baseada em EMAs / preço.
  - `build_indicators_for_symbol(symbol)`.

- `bot_risk.py`
  - `calculate_bot_equity_usdt(bot, session)`: soma saldo USDT + valor das moedas.
  - `check_stop_loss(bot, session)`: desativa bot e grava log STOP se exceder perda.

- `bot_rebalance.py`
  - `rebalance_bot(bot, session, target_per_asset_usdt=10.0)`:
    - calcula valor total do bot,
    - distribui alvo de 10 USDT por ativo,
    - usa excedentes e USDT para corrigir,
    - marca `last_rebalance_insufficient`.

- `bot_engine.py`
  - (planejado para rodar em background, hoje acionamos mais manualmente)
  - Ciclo:
    - lê bot ativo,
    - obtém análise e oportunidade,
    - dependendo de `trade_mode`:
      - SIMULATED → chama `simulate-trade`,
      - REAL_MARKET_SPOT → chama endpoint de market-swap.

## Frontend

- SPA em React:
  - `App.jsx`: layout geral.
  - `BotsList.jsx`: lista bots + seletor de ativo.
  - `ActiveBotPanel.jsx`:
    - mostra bot ativo, modo (simulado/real), saldo, stop-loss, rebalance info.
    - mostra toggle de modo, botão de rebalance (futuro), etc.
  - `ActiveBotAssets.jsx`:
    - lista de moedas do bot com:
      - preço inicial,
      - preço atual,
      - variação,
      - `buy_percent`, `sell_percent`, flags `can_buy`/`can_sell`.
  - `ActiveBotMarketStatus.jsx`:
    - indicadores por moeda (RSI, EMA, tendência).
  - `ActiveBotOpportunity.jsx`:
    - mostra par sugestão (sell_symbol / buy_symbol) ou “sem oportunidade”.
  - `ActiveBotLogs.jsx`:
    - lista de logs com side, símbolos, quantias e mensagem.
  - `FooterInfo.jsx`:
    - notas sobre indicadores, teste vs produção, etc.

---

## 3.3. `docs/backend-api.md`

Aqui vai um resumo dos endpoints principais, focando no que você usa com `curl`.

```md
# API Backend – bbot

Base: `http://localhost:8000`

## Health

- `GET /api/health`
  - Retorna `{ "status": "ok", "service": "binance-trade-backend" }`.

## Bots

### Listar bots

- `GET /api/bots/`

### Criar bot

- `POST /api/bots/`
  - Body JSON:
    - `name` (string)
    - `initial_balance_usdt` (float)
    - `current_balance_usdt` (float) – geralmente igual ao inicial na criação
    - opcional: `stop_loss_percent` (float, default 40.0)
    - opcional: `trade_mode` (`SIMULATED` / `REAL_MARKET_SPOT`, default `SIMULATED`)

### Detalhes de um bot

- `GET /api/bots/{bot_id}`

### Ativar / desativar

- `PATCH /api/bots/{bot_id}/activate`
- `PATCH /api/bots/{bot_id}/deactivate`
  - A ativação garante que só exista **um bot ativo** por vez.

### Atualizar bot (stop-loss, saldo inicial, etc.)

- `PATCH /api/bots/{bot_id}`
  - Body JSON (parciais):
    - `initial_balance_usdt`
    - `stop_loss_percent`
    - outros campos simples (dependendo da implementação atual).

### Modo de trade

- `PATCH /api/bots/{bot_id}/trade-mode`
  - Body:
    - `{ "trade_mode": "SIMULATED" }` ou `{ "trade_mode": "REAL_MARKET_SPOT" }`

### Rebalance

- `POST /api/bots/{bot_id}/rebalance/`
  - Opcional: `{ "target_per_asset_usdt": 10.0 }`
  - Resultado indica:
    - valor total antes/depois,
    - se houve `insufficient_funds`.

## Ativos do Bot (moedas)

- `GET /api/bots/{bot_id}/assets/`
- `POST /api/bots/{bot_id}/assets/`
  - Body:
    - `symbol` (ex. `"ETH"`)
    - opcional (na versão atual pode ser obrigatório dependendo do código):
      - `buy_percent` (ex.: `-5`)
      - `sell_percent` (ex.: `10`)
- `PATCH /api/bots/{bot_id}/assets/{asset_id}`
  - para ajustar `buy_percent`, `sell_percent`, flags, etc.

## Análise e indicadores

- `GET /api/bots/{bot_id}/analysis/`
  - Retorna:
    - `assets[]` com:
      - `initial_price_usdt`
      - `current_price_usdt`
      - `change_percent`
      - `can_buy_now` / `can_sell_now`
      - thresholds configurados.
- `GET /api/bots/{bot_id}/opportunity/`
  - Retorna:
    - `has_opportunity`
    - `sell_symbol`, `buy_symbol`
    - variações associadas
    - mensagem textual.

- `GET /api/bots/{bot_id}/indicators/`
  - Retorna, por ativo:
    - `price_usdt`
    - `rsi_14`
    - `ema_fast`, `ema_slow`
    - `trend`

## Trades e logs

### Simulação

- `POST /api/bots/{bot_id}/simulate-trade/`
  - Usa:
    - par escolhido por `/opportunity/`
    - `trade_unit_usdt` (hoje fixo em 10, ou próximo disso)
  - Atualiza:
    - `reserved_amount` das moedas,
    - `initial_price_usdt` após o trade,
    - `TradeLog` com `side="SIMULATED_SWAP"`.

### Trade real (market swap via USDT)

- `POST /api/bots/{bot_id}/trade/market-swap/`
  - Body:
    - `sell_symbol`
    - `buy_symbol`
    - `trade_unit_usdt` (ex.: `10`)
  - Regras:
    - Vende `sell_symbol` em MARKET para USDT (respeitando LOT_SIZE, MIN_NOTIONAL).
    - Compra `buy_symbol` com USDT recebido.
    - Atualiza `reserved_amount` e `initial_price_usdt`.
    - Cria `TradeLog`.

### Logs

- `GET /api/bots/{bot_id}/logs/`
  - Lista ordenada por data desc, com:
    - `side`, `from_symbol`, `to_symbol`,
    - `amount_from`, `amount_to`,
    - `price_usdt`,
    - `message`.

