# BBOT – ARCHITECTURE

Este documento descreve a arquitetura técnica do BBOT, incluindo componentes, fluxos de dados e responsabilidades de cada camada.

---

## Visão geral

O BBOT é um sistema monolítico containerizado que inclui:

- Backend:
  - API REST com FastAPI;
  - Persistência com SQLModel + SQLite;
  - Integração com a API REST da Binance (testnet ou produção);
  - Lógica de risco, rebalance, análise e execução de trades.

- Frontend:
  - SPA em React (Vite);
  - Interface única que exibe um painel de bot e suas moedas.

- Infraestrutura:
  - Docker com imagem única;
  - Arquivo SQLite montado via volume;
  - `.env` com configuração de ambiente e chaves da Binance.

---

## Backend

### Tecnologias

- Python 3.11
- FastAPI
- SQLModel (sobre SQLAlchemy)
- SQLite (arquivo `data/bot.db`)
- Cliente da Binance (REST) via biblioteca oficial ou HTTP customizado
- Uvicorn como servidor ASGI

### Arquivos principais

Os nomes exatos podem variar, mas a arquitetura geral é:

- `main.py`
  - Cria a instância FastAPI.
  - Configura CORS.
  - Inicializa o banco de dados.
  - Inclui routers:
    - `routes_bots`
    - `routes_bot_assets`
    - `routes_bot_analysis`
    - `routes_trade_logs`
    - `routes_bot_trade`
    - `routes_bot_simtrade`
    - `routes_bot_rebalance`

- `database.py`
  - Cria engine do SQLModel apontando para `data/bot.db`.
  - Expõe `SessionLocal` para uso nas rotas.
  - Função para criar tabelas (caso necessário).

- `models.py`
  - Define modelos:
    - `Bot`
    - `BotAsset`
    - `TradeLog`
  - Cada modelo possui campos relacionados a:
    - IDs,
    - timestamps,
    - parâmetros de trade e risco,
    - relacionamentos lógicos via `bot_id`.

- `binance_client.py`
  - Configuração de:
    - base URL de testnet / produção;
    - leitura de `BINANCE_API_KEY`, `BINANCE_API_SECRET`, `BINANCE_TESTNET`.
  - Funções:
    - obter preços (`get_symbol_price_usdt`);
    - validar símbolos (`validate_symbol_usdt` ou similar);
    - obter klines para indicadores;
    - obter filtros de negociação (LOT_SIZE, MIN_NOTIONAL);
    - ajustar quantidade para os filtros;
    - enviar ordens MARKET (buy/sell).

- `indicators.py`
  - Lógica para cálculo de:
    - RSI(14);
    - EMAs;
    - tendência;
    - possível combinação desses indicadores para status da moeda.

- `bot_risk.py`
  - Lógica de risco:
    - cálculo de equity total do bot em USDT;
    - verificação de stop-loss;
    - disparo de eventos de parada e logs de tipo `STOP`.

- `bot_rebalance.py`
  - Lógica de rebalance:
    - cálculo do valor total do bot;
    - distribuição alvo de ~10 USDT por moeda;
    - reatribuição de saldos virtuais;
    - marcação de rebalance insuficiente, se aplicável.

- `bot_engine.py`
  - Lógica de engine:
    - leitura de bot ativo;
    - análise de oportunidade de trade;
    - decisão de acionar:
      - simulação de trade; ou
      - trade real;
    - acionamento de rebalance em intervalo configurável.

- `routes_bots.py`
  - Rotas:
    - criação de bot;
    - listagem;
    - ativação / desativação;
    - atualização de parâmetros (stop-loss, trade_mode, etc.).

- `routes_bot_assets.py`
  - Rotas:
    - adicionar moedas a um bot;
    - listar moedas de um bot;
    - atualização de parâmetros de uma moeda;
    - (possivelmente) remoção de moeda.

- `routes_bot_analysis.py`
  - Rotas:
    - análise do bot (`/analysis`);
    - oportunidade (`/opportunity`);
    - indicadores (`/indicators`).

- `routes_trade_logs.py`
  - Rotas:
    - listagem de logs de trade para um bot.

- `routes_bot_trade.py`
  - Rotas:
    - execução de trade real market swap via USDT.

- `routes_bot_simtrade.py`
  - Rotas:
    - execução de trade simulado entre moedas via USDT.

- `routes_bot_rebalance.py`
  - Rotas:
    - rebalance manual para determinado bot.

---

## Frontend

### Tecnologias

- React
- Vite
- JavaScript (ou TypeScript, conforme o repositório)
- CSS simples (inline, módulos ou global)

### Estrutura

- `index.html`
- `src/main.jsx`
- `src/App.jsx`
- `src/components/`
  - `BotsList.jsx`
  - `ActiveBotPanel.jsx`
  - `ActiveBotAssets.jsx`
  - `ActiveBotMarketStatus.jsx`
  - `ActiveBotOpportunity.jsx`
  - `ActiveBotLogs.jsx`
  - `FooterInfo.jsx`

O frontend comunica-se com o backend via fetch/XHR, usando as rotas documentadas em `API_REFERENCE.md`.

---

## Banco de dados

- SQLite, com arquivo armazenado em:
  - `data/bot.db`
- O arquivo é montado como volume no Docker para persistência entre execuções.
- Tabelas principais:
  - `bot` (instâncias de bots);
  - `botasset` (moedas associadas a cada bot);
  - `tradelog` (logs de operações).

---

## Docker e ambiente

- Dockerfile:
  - base: `python:3.11-slim` (ou similar);
  - instala dependências Python (via `backend/requirements.txt`);
  - instala e builda o frontend (`npm install && npm run build`);
  - copia o build estático para pasta servida pelo backend;
  - inicia o Uvicorn com a app FastAPI.

- `.env`:
  - principais variáveis:
    - `BINANCE_TESTNET` (true/false);
    - `BINANCE_API_KEY`;
    - `BINANCE_API_SECRET`;
    - `BOT_ENGINE_INTERVAL_SECONDS`;
    - `BOT_REBALANCE_INTERVAL_SECONDS`.

---

## Fluxos principais

### Criação de bot

1. Cliente chama `POST /api/bots/`.
2. FastAPI cria um novo registro em `Bot`.
3. `initial_balance_usdt` e `current_balance_usdt` são definidos.
4. Bot começa, por padrão, em `trade_mode = SIMULATED` e `is_active = false`.

### Ativação de bot

1. Cliente chama `PATCH /api/bots/{id}/activate`.
2. Backend desativa qualquer outro bot ativo.
3. Marca o bot como `is_active = true`.

### Adição de moeda ao bot

1. Cliente chama `POST /api/bots/{id}/assets/`.
2. Backend valida o símbolo na Binance.
3. Obtém preço atual em USDT.
4. Define `initial_price_usdt`.
5. Atribui `reserved_amount` equivalente a ~10 USDT (se possível).
6. Salva `BotAsset`.

### Análise de bot

1. Cliente chama `GET /api/bots/{id}/analysis/`.
2. Backend lê `Bot` e `BotAsset`s.
3. Obtém preços atuais na Binance.
4. Calcula variações e flags `can_buy_now`, `can_sell_now`.
5. Retorna lista de assets com informações consolidadas.

### Detecção de oportunidade

1. Cliente chama `GET /api/bots/{id}/opportunity/`.
2. Backend usa análise para:
   - identificar moedas em zona de venda;
   - identificar moedas em zona de compra.
3. Seleciona o par mais vantajoso (regra simples definida em código).
4. Retorna sugestão de trade ou mensagem de “nenhuma oportunidade”.

### Execução de trade (simulada ou real)

1. Cliente (ou engine) chama:
   - `/simulate-trade/` para simulado; ou
   - `/trade/market-swap/` para real.
2. Backend:
   - calcula quantidades,
   - ajusta para filtros,
   - atualiza saldos,
   - registra log.
3. No modo real, envia ordens à Binance e trata respostas.

---

## Considerações para manutenção e evolução

- Os módulos devem ser mantidos coesos:
  - rotas não devem conter lógica pesada de negócio;
  - lógica de risco, rebalance e trade deve estar em arquivos próprios.

- Qualquer novo comportamento deve ser avaliado em função de:
  - não violar as restrições de segurança do projeto;
  - manter a compatibilidade com o escopo descrito em `PROJECT_SCOPE.md`.

- Recomenda-se manter a documentação em sincronia com refatorações de:
  - nomes de arquivos;
  - endpoints;
  - modelos de dados.
