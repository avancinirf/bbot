# BBOT – BACKLOG

Este documento organiza o que já foi feito, o que está em andamento e o que está pendente, com prioridades.

As prioridades são:

- P0: crítico/urgente.
- P1: importante.
- P2: melhoria.
- P3: longo prazo / ideia.

---

## 1. Backend

### 1.1 Implementado (concluído)

- [x] P0 – CRUD de bots (`/api/bots/`).
- [x] P0 – Ativar/desativar bot, garantindo apenas um ativo.
- [x] P0 – CRUD básico de assets (`/api/bots/{id}/assets/`).
- [x] P0 – Integração com Binance para:
  - preços (`XXXUSDT`);
  - klines para indicadores;
  - filtros de exchange.
- [x] P0 – Análise por bot (`/analysis`).
- [x] P0 – Detecção de oportunidade (`/opportunity`).
- [x] P0 – Cálculo de indicadores (`/indicators`).
- [x] P0 – Registro de logs (`/logs`).
- [x] P0 – Execução de trade simulado (`/simulate-trade/`).
- [x] P0 – Execução de trade real MARKET SPOT (`/trade/market-swap/`).
- [x] P1 – Rebalance manual (`/rebalance/`).
- [x] P1 – Stop-loss com desativação do bot.
- [x] P1 – Uso de `.env` para configurar Binance e intervals.
- [x] P1 – Suporte a modos de trade:
  - `SIMULATED`;
  - `REAL_MARKET_SPOT`.

### 1.2 Em andamento / parcialmente implementado

- [ ] P1 – Tratamento completo de excedentes de moeda como “saldo adicional” do bot.
- [ ] P1 – Lógica consolidada de rebalance considerando:
  - saldo insuficiente de USDT;
  - marcação consistente de `last_rebalance_insufficient`.

### 1.3 Pendente

- [ ] P0 – Engine automática de trade:
  - loop contínuo com:
    - análise;
    - oportunidade;
    - decisão baseada em `trade_mode`;
  - respeito a `BOT_ENGINE_INTERVAL_SECONDS`.
- [ ] P1 – Política clara de “vender tudo” ou apenas “parar” quando o stop-loss for atingido, configurável por bot.
- [ ] P1 – Parametrizar `trade_unit_usdt` por bot e/ou por moeda.
- [ ] P2 – Adicionar modos adicionais no futuro (ex.: LIMIT), mantendo separação clara de lógica.
- [ ] P3 – Adicionar suporte a backtesting usando dados históricos.

---

## 2. Frontend

### 2.1 Implementado

- [x] P0 – Dashboard com:
  - bot ativo;
  - lista de bots.
- [x] P0 – Painel de ativos com:
  - preço inicial;
  - preço atual;
  - variação percentual;
  - indicação visual de alta/baixa.
- [x] P1 – Exibição de indicadores por moeda.
- [x] P1 – Exibição de oportunidade atual do bot.
- [x] P1 – Listagem de logs de trade.
- [x] P0 – Formulário de criação de bot na UI:
  - nome;
  - saldo inicial;
  - stop-loss;
  - modo inicial (default: SIMULATED).
- [x] P0 – Formulário de adição de moeda na UI:
  - símbolo;
  - `buy_percent` (default sugerido: -3%);
  - `sell_percent` (default sugerido: +5%);
  - validação simples (backend confirma símbolo via Binance).

### 2.2 Em andamento

- [ ] P1 – Exposição clara do `trade_mode` (SIMULATED vs REAL_MARKET_SPOT).
- [ ] P1 – Botões no painel do bot para:
  - alternar `trade_mode`;
  - chamar rebalance manual.

### 2.3 Pendente

- [ ] P1 – Edição de `buy_percent` e `sell_percent` diretamente na UI.
- [ ] P1 – Edição de flags `can_buy` / `can_sell` na UI.
- [ ] P2 – Indicação visual clara quando:
  - `last_rebalance_insufficient = true`.

- [ ] P2 – Exibição opcional de pequenos gráficos ou mini-sparkline por moeda (futuro).

---

## 3. Engine e automação

### 3.1 Implementado

- [x] P1 – Estrutura de bot_engine (arquivo e conceitos).

### 3.2 Pendente

- [ ] P0 – Loop automático e estável que:
  - recebe o bot ativo;
  - verifica stop-loss;
  - obtém análise e oportunidade;
  - executa trade simulado/real conforme `trade_mode`.

- [ ] P1 – Configuração de intervalo via `.env`:
  - `BOT_ENGINE_INTERVAL_SECONDS`;
  - `BOT_REBALANCE_INTERVAL_SECONDS`.

- [ ] P2 – Possibilidade de engine ser ligada/desligada via API/UI.

---

## 4. Infraestrutura e DevX

### 4.1 Implementado

- [x] P0 – Docker único com backend + build do frontend.
- [x] P1 – Estratégia de volume para `data/bot.db`.
- [x] P1 – Uso de `.env` para API keys.

### 4.2 Pendente

- [ ] P2 – `env.example` documentado e alinhado com `SETUP.md`.
- [ ] P2 – Melhor estrutura de logs (arquivo, níveis, etc.).
- [ ] P3 – Scripts convenientes (ex.: `makefile` ou scripts npm/pip para rodar dev/prod).

---

## 5. Documentação

### 5.1 Implementado

- [x] P0 – OVERVIEW.md.
- [x] P0 – PROJECT_SCOPE.md.
- [x] P0 – ARCHITECTURE.md.
- [x] P0 – API_REFERENCE.md.
- [x] P0 – BACKEND_MODULES.md.
- [x] P0 – FRONTEND.md.
- [x] P0 – BACKLOG.md.
- [x] P0 – SETUP.md (a ser criado).
- [x] P0 – CONTRIBUTING.md (a ser criado).
- [x] P0 – SYSTEM_TREE.md (a ser criado).

### 5.2 Pendente

- [ ] P2 – Atualização contínua da documentação conforme o código evolui.
