# BBOT – FRONTEND

Este documento descreve a interface React do BBOT, seus componentes e interações com a API.

---

## Objetivo da interface

A UI é uma SPA simples, com foco em:

- mostrar o bot ativo e suas informações;
- listar bots e permitir alternar o foco/ativação;
- exibir as moedas do bot, suas variações e parâmetros;
- exibir indicadores de mercado;
- exibir logs de trade;
- exibir informações de oportunidade de trade.

A criação de bots e a adição de moedas podem, inicialmente, ser feitas via `curl`/API; formulários dedicados serão adicionados posteriormente.

---

## Estrutura geral

Arquivos principais:

- `src/main.jsx`
  - ponto de entrada da aplicação React;
  - renderiza `<App />`.

- `src/App.jsx`
  - layout geral da página:
    - cabeçalho com nome do sistema;
    - seção de lista de bots;
    - painel do bot ativo;
    - rodapé com informações auxiliares.

---

## Componentes

### BotsList.jsx

Responsabilidade:

- listar bots existentes via `GET /api/bots/`;
- destacar o bot ativo;
- permitir selecionar um bot para ver detalhes;
- expor ações como:
  - ativar/desativar (via endpoints de backend);
  - futuramente, editar nome, excluir, etc.

Interações típicas:

- ao clicar em um bot, dispara callback para definir “bot selecionado” no estado global do App;
- ao clicar em um botão de ativar, chama `PATCH /api/bots/{id}/activate`.

---

### ActiveBotPanel.jsx

Responsabilidade:

- exibir informações do bot atualmente ativo (ou selecionado):
  - nome;
  - status (ativo/inativo);
  - `trade_mode` (SIMULATED/REAL_MARKET_SPOT);
  - `initial_balance_usdt` vs `current_balance_usdt`;
  - `stop_loss_percent`;
  - informações de rebalance:
    - `last_rebalance_at`;
    - `last_rebalance_insufficient`.

- expor controles:
  - botão para ativar/desativar;
  - botão para alternar `trade_mode` (SIMULATED ↔ REAL_MARKET_SPOT);
  - botão para acionar rebalance manual (chamando `/rebalance/`).

Interações:

- usa `GET /api/bots/{id}` para atualizar informações;
- usa:
  - `PATCH /api/bots/{id}/activate`;
  - `PATCH /api/bots/{id}/deactivate`;
  - `PATCH /api/bots/{id}/trade-mode`;
  - `POST /api/bots/{id}/rebalance/`.

---

### ActiveBotAssets.jsx

Responsabilidade:

- listar ativos de um bot via `GET /api/bots/{id}/assets/`;
- exibir, para cada moeda:
  - símbolo;
  - preço inicial em USDT;
  - preço atual em USDT (obtido por análise ou endpoint dedicado);
  - variação percentual;
  - seta verde/vermelha e formatação condicional;
  - `buy_percent` e `sell_percent`;
  - flags `can_buy` / `can_sell`.

Visualmente:

- separar visualmente moedas em:
  - em zona de compra;
  - em zona de venda;
  - neutras.

Interações futuras:

- permitir edição inline de `buy_percent` e `sell_percent`;
- permitir desativar `can_buy` / `can_sell`.

---

### ActiveBotMarketStatus.jsx

Responsabilidade:

- exibir indicadores por moeda, obtidos de:
  - `GET /api/bots/{id}/indicators/`.

Para cada moeda:

- `symbol`;
- `price_usdt`;
- `rsi_14`;
- `ema_fast`;
- `ema_slow`;
- `trend`.

Também deve exibir um pequeno texto explicativo:

- o que é RSI;
- o que é EMA;
- como esses indicadores influenciam a decisão do bot.

---

### ActiveBotOpportunity.jsx

Responsabilidade:

- exibir, de forma clara, se há uma oportunidade de trade.

Obtém dados via:

- `GET /api/bots/{id}/opportunity/`.

Quando `has_opportunity = true`:

- mostra:
  - `sell_symbol`;
  - `buy_symbol`;
  - variações associadas;
  - mensagem informativa.

Quando não há oportunidade:

- exibe mensagem amigável de “nenhuma oportunidade no momento”.

---

### ActiveBotLogs.jsx

Responsabilidade:

- listar logs de trade via `GET /api/bots/{id}/logs/`.

Para cada log:

- `created_at`;
- `side` (SIMULATED_SWAP, REAL_SWAP, SELL, STOP, etc.);
- `from_symbol` → `to_symbol`;
- `amount_from`, `amount_to`;
- `price_usdt`;
- `message`.

Essa listagem é importante para auditoria e depuração.

---

### FooterInfo.jsx

Responsabilidade:

- exibir notas fixas, por exemplo:
  - uso de testnet vs produção;
  - explicações sobre:
    - `trade_unit_usdt` (hoje 10 USDT);
    - stop-loss;
    - diferença entre modo simulado e modo real;
    - importância de usar API keys de trade apenas (sem permissão de saque).

---

## Integração com a API

- Todas as chamadas devem usar URLs relativas (`/api/...`) para funcionar bem dentro do container.
- A aplicação não deve conhecer diretamente:
  - chaves da Binance;
  - detalhes de testnet vs produção;
- Esses detalhes são responsabilidade do backend.

---

## Pendências planejadas

- Formulário de criação de bot:
  - permitir criar bot da interface, sem `curl`.

- Formulário de adição de moeda:
  - selecionar símbolo (ex.: input + validação no backend);
  - configurar `buy_percent` e `sell_percent` com defaults.

- Edição interativa de thresholds:
  - ajustar percentuais direto na lista de moedas.

- Exibição visual do modo:
  - diferenciar clara e visualmente:
    - modo SIMULATED;
    - modo REAL_MARKET_SPOT.

- Indicação de rebalance insuficiente:
  - tag visual quando `last_rebalance_insufficient = true`.

---

## Boas práticas de UI

- Evitar expor termos técnicos internos (como nomes de campos do modelo);
- Dar foco em:
  - saldo do bot;
  - variação por moeda;
  - oportunidades;
  - modo de operação;
  - logs de ações.

Qualquer evolução deve manter a página única, simples e legível, alinhada ao foco do projeto.
