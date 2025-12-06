# bbot – Binance Microtrade Bot

Projeto em desenvolvimento para gerenciamento de **bots de microtrade** na Binance, com:

- Backend em **Python (FastAPI + SQLModel + SQLite)**
- Futuro frontend em **React**
- Execução em **um único container Docker** (backend + frontend no mesmo container)
- Moeda de referência: **USDT**
- Foco em **segurança** (sem permissão de saque na API) e **modo simulado** para testes

---

## 1. Objetivos do projeto

- Criar um sistema local (MacBook Pro M1) para:
  - Gerenciar **múltiplos bots de microtrade** operando na **Binance Spot (tipo de ordem: market)**;
  - Usar **saldo virtual por bot** (limite definido manualmente, sem depender de todo o saldo da conta);
  - Utilizar **métricas de mercado e indicadores técnicos** para auxiliar decisão de compra/venda;
  - Registrar todas as **transações e contexto de decisão** (indicadores, regras aplicadas);
  - Expor uma interface web simples (frontend React) para:
    - Criar/editar bots,
    - Ligar/desligar bots,
    - Bloquear/desbloquear bots,
    - Visualizar indicadores em tempo real,
    - Listar transações (P/L vem depois).

---

## 2. Requisitos funcionais (resumo)

### 2.1. Sistema / Ambiente

- Rodar em **um único container Docker**:
  - Backend FastAPI + engine dos bots + futuro frontend React.
- Banco de dados: **SQLite** (arquivo em `./data`).
- Desenvolvimento local em **MacBook Pro M1**.
- Integração com **Binance Spot API**:
  - Apenas **trades** (Spot);
  - **Sem permissão de saque** (withdrawals desabilitados na API key).

### 2.2. Modo de execução

- **Modo simulado** (implementado):
  - Usa dados reais de mercado (candles 5m da Binance);
  - Simula ordens e saldos no banco de dados;
  - Não envia ordens reais para a Binance.
- **Modo real** (planejado):
  - Enviar ordens spot market reais;
  - Ainda assim respeitando o **saldo virtual por bot**.

### 2.3. Bots

Cada bot tem:

- `name`: nome amigável;
- `status`: `online` / `offline` / `blocked`;
- `saldo_usdt_limit`: limite máximo de USDT que o bot pode usar (saldo virtual do bot);
- `saldo_usdt_livre`: saldo livre virtual atual do bot;
- `stop_loss_percent`: stop global do bot em %, negativo (ex.: `-20` = -20%);
- Flags:
  - `comprar_ao_iniciar` (bool):
    - Se `true`, ao ligar o bot, compra o valor de trade (ex.: 10 USDT) da moeda configurada se não tiver posição;
  - `compra_mercado` (bool):
    - Se `true`, só compra se o índice de mercado indicar compra/neutro;
  - `venda_mercado` (bool):
    - Se `true`, só vende se o índice de mercado indicar venda/neutro.

### 2.4. Pares por bot

Lista inicial de pares suportados:

```text
BTC/USDT, ETH/USDT, SOL/USDT, XRP/USDT, XLM/USDT,
ASTR/USDT, SUI/USDT, ADA/USDT, NEAR/USDT, APT/USDT,
FET/USDT, LINK/USDT, AVAX/USDT, HBAR/USDT, BCH/USDT,
DOGE/USDT, AAVE/USDT, ENA/USDT, ZEC/USDT, DASH/USDT


## 2. Requisitos funcionais (resumo)

### 2.1. Sistema / Ambiente

- Rodar em **um único container Docker**:
  - Backend FastAPI + engine dos bots + futuro frontend React.
- Banco de dados: **SQLite** (arquivo em `./data`).
- Desenvolvimento local em **MacBook Pro M1**.
- Integração com **Binance Spot API**:
  - Apenas **trades** (Spot);
  - **Sem permissão de saque** (withdrawals desabilitados na API key).

### 2.2. Modo de execução

- **Modo simulado** (implementado):
  - Usa dados reais de mercado (candles 5m da Binance);
  - Simula ordens e saldos no banco de dados;
  - Não envia ordens reais para a Binance.
- **Modo real** (planejado):
  - Enviar ordens spot market reais;
  - Ainda assim respeitando o **saldo virtual por bot**.

### 2.3. Bots

Cada bot tem:

- `name`: nome amigável;
- `status`: `online` / `offline` / `blocked`;
- `saldo_usdt_limit`: limite máximo de USDT que o bot pode usar (saldo virtual do bot);
- `saldo_usdt_livre`: saldo livre virtual atual do bot;
- `stop_loss_percent`: stop global do bot em %, negativo (ex.: `-20` = -20%);
- Flags:
  - `comprar_ao_iniciar` (bool):
    - Se `true`, ao ligar o bot, compra o valor de trade (ex.: 10 USDT) da moeda configurada se não tiver posição;
  - `compra_mercado` (bool):
    - Se `true`, só compra se o índice de mercado indicar compra/neutro;
  - `venda_mercado` (bool):
    - Se `true`, só vende se o índice de mercado indicar venda/neutro.

### 2.4. Pares por bot

Lista inicial de pares suportados:

    BTC/USDT, ETH/USDT, SOL/USDT, XRP/USDT, XLM/USDT,
    ASTR/USDT, SUI/USDT, ADA/USDT, NEAR/USDT, APT/USDT,
    FET/USDT, LINK/USDT, AVAX/USDT, HBAR/USDT, BCH/USDT,
    DOGE/USDT, AAVE/USDT, ENA/USDT, ZEC/USDT, DASH/USDT

Para cada par (`BotPair`):

- `symbol`: ex.: `BTCUSDT`;
- `valor_de_trade_usdt`: valor da ordem (em USDT), ex.: 10;
- `valor_inicial`: preço da última compra/venda ou quando foi configurado;
- `porcentagem_compra`:
  - `0` → regra desativada;
  - valor **negativo** (ex.: `-5`) → só compra se o preço atual estiver **pelo menos X% abaixo** do `valor_inicial`;
- `porcentagem_venda`:
  - `0` → regra desativada;
  - valor **positivo** (ex.: `5`) → só vende se o preço atual estiver **pelo menos X% acima** do `valor_inicial`;
- **Estado da posição**:
  - `has_open_position` (bool);
  - `qty_moeda` (quantidade);
  - `last_buy_price`, `last_sell_price`.

**Restrição**:  
> **Uma posição por moeda por bot** – compra, depois vende; só compra de novo após vender.


## 3. Estratégia de decisão (regras de compra/venda)

### 3.1. Quando comprar?

Para cada par do bot:

1. Se `comprar_ao_iniciar = 1` **e**:
   - bot está com `status = online`;
   - não há posição aberta nesse par (`has_open_position = false`);
   - `valor_inicial` é `null` (nunca comprou);
   - `saldo_usdt_livre >= valor_de_trade_usdt`;

   então o bot **compra automaticamente** o valor de trade (ex.: 10 USDT) dessa moeda, **ignorando as demais regras**.

2. Regra `porcentagem_compra`:
   - Se `porcentagem_compra != 0` **e** `valor_inicial` definido:
     - calcular `var_pct = (valor_atual - valor_inicial) / valor_inicial * 100`;
     - só pode comprar se `var_pct <= porcentagem_compra`
       (ex.: `porcentagem_compra = -5` → preço atual pelo menos 5% abaixo de `valor_inicial`).
   - Se `porcentagem_compra == 0`, essa regra é ignorada.

3. Regra `compra_mercado`:
   - Se `compra_mercado = 1`:
     - só compra se `market_signal_compra == true`
       (índice de tendência neutro ou favorável à compra).
   - Se `compra_mercado = 0`, essa regra é ignorada.

4. Regras gerais de compra:
   - não pode haver posição aberta nesse par;
   - é obrigatório `saldo_usdt_livre >= valor_de_trade_usdt`.

A função de compra só autoriza a operação se **todas** as regras aplicáveis forem satisfeitas.

---

### 3.2. Quando vender?

Para cada par com posição aberta:

1. Regra `porcentagem_venda`:
   - Se `porcentagem_venda > 0`:
     - definir `base_price = valor_inicial` (ou `last_buy_price` quando existir);
     - calcular `var_pct = (valor_atual - base_price) / base_price * 100`;
     - só vende se `var_pct >= porcentagem_venda`
       (ex.: `porcentagem_venda = 5` → preço atual pelo menos 5% acima de `base_price`).
   - Se `porcentagem_venda == 0`, essa regra é ignorada.

2. Regra `venda_mercado`:
   - Se `venda_mercado = 1`:
     - só vende se `market_signal_venda == true`
       (índice de tendência neutro ou favorável à venda).
   - Se `venda_mercado = 0`, essa regra é ignorada.

3. Regras gerais de venda:
   - deve existir posição aberta (`has_open_position = true`);
   - `qty_moeda > 0`.

A função de venda só autoriza a operação se **todas** as regras aplicáveis forem satisfeitas.

---

### 3.3. Stop loss por bot

- Cada bot possui `stop_loss_percent` (valor negativo, ex.: `-20`).
- Regra atual (simplificada, por par):
  - Para cada par com posição aberta:
    - se existir `last_buy_price` e indicador recente para o símbolo;
    - calcula `var_pct = (valor_atual - last_buy_price) / last_buy_price * 100`;
    - se `var_pct <= stop_loss_percent`, o **stop loss do bot é disparado**.

Quando o stop loss é disparado:

1. O sistema vende **todas as posições abertas** do bot (venda simulada a preço de mercado).
2. Atualiza o saldo virtual (`saldo_usdt_livre`).
3. Define `status` do bot como `blocked`.
4. Registra as operações como trades com motivo `"stop_loss_triggered"`.

Depois disso, o bot fica bloqueado até ser manualmente alterado para outro status.


## 4. Indicadores e métrica de tendência

Candles: **5 minutos** (`5m`) por par/símbolo.

Para cada símbolo (ex.: `BTCUSDT`) são calculados:

- `close`: preço de fechamento do candle.
- `ema9`: média móvel exponencial de 9 períodos.
- `ema21`: média móvel exponencial de 21 períodos.
- `rsi14`: RSI de 14 períodos.
- `macd`, `macd_signal`, `macd_hist`: MACD com parâmetros (12, 26, 9).
- `adx`: ADX de 14 períodos (força da tendência).

Esses valores são salvos na tabela de indicadores (`indicator`) para cada candle.

---

### 4.1. Índice de tendência (trend_score e trend_label)

A partir dos indicadores, é calculado um índice simplificado de tendência:

1. **Score base (`trend_score`)**:
   - Soma contribuições de:
     - `ema9 > ema21` → +1 (tendência de alta); caso contrário → -1.
     - `macd > macd_signal` → +1 (alta); caso contrário → -1.

2. **Ajuste pela força da tendência (ADX)**:
   - Se `adx > 25` → multiplica o score por 1.5 (tendência forte).
   - Se `adx < 20` → multiplica o score por 0.5 (mercado lateral).

3. **Label (`trend_label`)**:
   - `bullish` se `trend_score >= 1`.
   - `bearish` se `trend_score <= -1`.
   - `neutral` caso contrário.

---

### 4.2. Sinais de mercado para compra e venda

Com base em `trend_label` e `rsi14`, são definidos:

- `market_signal_compra`:
  - `true` quando:
    - `trend_label == 'bullish'`, ou
    - `trend_label == 'neutral'` e `rsi14` entre 40 e 60 (zona neutra).
  - `false` nos demais casos.

- `market_signal_venda`:
  - `true` quando:
    - `trend_label == 'bearish'`, ou
    - `trend_label == 'neutral'` e `rsi14` entre 40 e 60.
  - `false` nos demais casos.

Esses campos (`market_signal_compra` e `market_signal_venda`) são usados diretamente nas regras:

- `compra_mercado = 1` → só compra se `market_signal_compra == true`.
- `venda_mercado = 1` → só vende se `market_signal_venda == true`.


## 5. Banco de dados (SQLite)

### 5.1. Tabelas principais

- `systemstate`
  - `id` (fixo 1)
  - `online` (global on/off do sistema)
  - `simulation_mode` (modo simulado x real)
  - `created_at`, `updated_at`

- `bot`
  - `id`, `name`
  - `status` (`online` / `offline` / `blocked`)
  - `saldo_usdt_limit`, `saldo_usdt_livre`
  - `stop_loss_percent`
  - `comprar_ao_iniciar`, `compra_mercado`, `venda_mercado`
  - `created_at`, `updated_at`

- `botpair`
  - `id`
  - `bot_id` (FK → `bot`)
  - `symbol` (ex.: `BTCUSDT`)
  - `valor_de_trade_usdt`
  - `valor_inicial`
  - `porcentagem_compra`, `porcentagem_venda`
  - `has_open_position`, `qty_moeda`
  - `last_buy_price`, `last_sell_price`
  - `created_at`, `updated_at`

- `trade`
  - `id`, `bot_id`, `bot_pair_id`, `symbol`
  - `side` (`BUY` / `SELL`)
  - `qty`, `price`, `value_usdt`, `fee_usdt`
  - `pnl_usdt` (para vendas)
  - `indicator_snapshot` (JSON string com indicadores)
  - `rule_snapshot` (texto com o motivo da decisão)
  - `binance_order_id` (quando for ordem real)
  - `created_at`

- `candle`
  - `id`
  - `symbol`
  - `open_time`
  - `open`, `high`, `low`, `close`, `volume`
  - `created_at`

- `indicator`
  - `id`
  - `symbol`, `open_time`
  - `close`
  - `ema9`, `ema21`, `rsi14`
  - `macd`, `macd_signal`, `macd_hist`
  - `adx`
  - `trend_score`, `trend_label`
  - `market_signal_compra`, `market_signal_venda`
  - `created_at`

---

## 6. Arquitetura do backend

### 6.1. Stack

- **FastAPI** – API REST.
- **SQLModel + SQLite** – ORM + banco embutido.
- **binance-connector** – cliente oficial da Binance (Spot).
- **pandas + numpy** – cálculo de indicadores técnicos.
- Tudo rodando em **um único container Docker**.

### 6.2. Organização de pastas

Estrutura simplificada:

    backend/
      app/
        api/
          system.py     # estado global (online/simulation_mode)
          bots.py       # bots, pares, trades, run_cycle
          market.py     # candles 5m, indicadores, sync com Binance
        bots/
          engine.py     # motor de decisão do bot (modo simulado)
        binance_client/
          client.py     # wrapper do binance-connector (klines 5m)
        core/
          config.py     # Settings (env, DB URL, API keys, flags)
        db/
          models.py     # SystemState, Bot, BotPair, Trade, Candle, Indicator
          session.py    # engine SQLite, init_db(), get_session()
        indicators/
          ta.py         # EMA, RSI, MACD, ADX, índice de tendência
      requirements.txt
    Dockerfile
    docker-compose.yml
    data/               # arquivos SQLite (volume, ignorado no git)
    .env                # configs locais (ignorado no git)

O estado global (`SystemState`) controla se o sistema está online e se está em modo simulado ou real.

---

## 7. APIs disponíveis (principal)

Base para desenvolvimento:

- `http://localhost:8000`

### 7.1. Health

- `GET /health`  
  Verifica se o servidor está de pé.

### 7.2. Sistema

- `GET /api/system/state`  
  Retorna o estado global (`online`, `simulation_mode`).

- `PUT /api/system/state`  
  Atualiza flags globais. Exemplo de payload:

    { "online": true, "simulation_mode": true }

### 7.3. Bots

- `GET /api/bots`  
  Lista todos os bots.

- `POST /api/bots`  
  Cria um novo bot.

- `GET /api/bots/{bot_id}`  
  Detalhes de um bot.

- `PUT /api/bots/{bot_id}`  
  Atualiza dados do bot.

- `POST /api/bots/{bot_id}/status`  
  Atualiza o status do bot (`online`, `offline`, `blocked`).

- `POST /api/bots/block_all`  
  Bloqueia todos os bots (status = `blocked`).

- `POST /api/bots/unblock_all`  
  Desbloqueia todos os bots bloqueados (voltam para `offline`).

- `GET /api/bots/available_pairs`  
  Lista estática de pares disponíveis para configuração.

- `GET /api/bots/{bot_id}/pairs`  
  Lista os pares configurados de um bot.

- `POST /api/bots/{bot_id}/pairs`  
  Adiciona um novo par a um bot.

- `PUT /api/bots/pairs/{pair_id}`  
  Atualiza configuração de um par (`valor_de_trade_usdt`, porcentagens).

- `POST /api/bots/{bot_id}/run_cycle`  
  Executa **1 ciclo** de decisão do bot em modo simulado  
  (aplica regras, compra/vende se necessário, registra trades).

- `GET /api/bots/{bot_id}/trades?limit=N`  
  Lista os últimos `N` trades do bot, mais recentes primeiro.

### 7.4. Mercado

- `POST /api/market/sync/{symbol}?limit=N`  
  Busca candles 5m na Binance para `{symbol}` (ex.: `BTCUSDT`),  
  salva em `candle` e recalcula indicadores em `indicator`.

- `GET /api/market/indicators/{symbol}?limit=N`  
  Retorna os últimos `N` indicadores calculados para `{symbol}`.

---

## 8. Como rodar localmente

### 8.1. Pré-requisitos

- Docker / Docker Desktop instalado.
- (Opcional) Git configurado para versionamento.

### 8.2. Subir o container

Na raiz do projeto:

    docker compose up --build

Endpoints úteis:

- `http://localhost:8000/health`
- `http://localhost:8000/docs` (Swagger da API)

### 8.3. Fluxo de teste rápido (modo simulado)

1. Colocar o sistema em **modo online + simulado**:

    curl -X PUT "http://localhost:8000/api/system/state" \
      -H "Content-Type: application/json" \
      -d '{"online": true, "simulation_mode": true}'

2. Criar um bot:

    curl -X POST "http://localhost:8000/api/bots" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "Bot BTC Base",
        "saldo_usdt_limit": 100,
        "stop_loss_percent": -20,
        "comprar_ao_iniciar": true,
        "compra_mercado": true,
        "venda_mercado": true
      }'

3. Adicionar o par `BTC/USDT`:

    curl -X POST "http://localhost:8000/api/bots/1/pairs" \
      -H "Content-Type: application/json" \
      -d '{
        "symbol": "BTC/USDT",
        "valor_de_trade_usdt": 10,
        "porcentagem_compra": -5,
        "porcentagem_venda": 5
      }'

4. Sincronizar mercado (candles + indicadores):

    curl -X POST "http://localhost:8000/api/market/sync/BTCUSDT?limit=200"

5. Colocar o bot em `online`:

    curl -X POST "http://localhost:8000/api/bots/1/status" \
      -H "Content-Type: application/json" \
      -d '{"status": "online"}'

6. Rodar um ciclo de decisão do bot:

    curl -X POST "http://localhost:8000/api/bots/1/run_cycle"

7. Ver os trades gerados:

    curl "http://localhost:8000/api/bots/1/trades?limit=10"
