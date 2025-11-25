# Frontend – UI do bbot

SPA em React, buildada com Vite e servida pelo backend em `/`.

## Estrutura

- `App.jsx`
  - Layout geral:
    - header com nome do sistema,
    - coluna lateral com lista de bots,
    - painel central com **bot ativo**,
    - rodapé com notas e informações de indicadores.

### Componentes principais

- `BotsList.jsx`
  - Chama `GET /api/bots/`.
  - Permite selecionar um bot como “focado” e mostrar detalhes.
  - Usa endpoints de ativar/desativar e trocar modo de trade (SIMULATED/REAL).

- `ActiveBotPanel.jsx`
  - Mostra:
    - nome do bot ativo,
    - `trade_mode` (SIMULATED/REAL),
    - saldo inicial vs saldo atual,
    - stop-loss e se já foi acionado,
    - info de rebalance:
      - data/hora do último rebalance,
      - flag `last_rebalance_insufficient`.
  - Botões:
    - ativar / desativar bot,
    - alternar trade_mode,
    - acionar rebalance (planejado).

- `ActiveBotAssets.jsx`
  - Lista os ativos do bot:
    - símbolo,
    - preço inicial,
    - preço atual (via `/analysis`),
    - variação (%),
    - setas verde/vermelha,
    - thresholds de buy/sell,
    - flags `buy on` / `sell on`.

- `ActiveBotMarketStatus.jsx`
  - Mostra para cada ativo:
    - RSI, EMA rápida/lenta, tendência.
  - Mostra também um pequeno bloco de explicação dos indicadores (nota em português).

- `ActiveBotOpportunity.jsx`
  - Mostra:
    - se há oportunidade (`has_opportunity`),
    - par sugerido: vender X, comprar Y,
    - texto com variações.

- `ActiveBotLogs.jsx`
  - Lista os logs do bot:
    - tipo (SIMULATED_SWAP, REAL_SWAP, STOP, etc.),
    - moedas de/para,
    - quantias,
    - timestamp,
    - mensagem.

- `FooterInfo.jsx`
  - Bloco com:
    - aviso de uso de testnet vs produção,
    - explicação resumida de:
      - trade_unit_usdt,
      - stop-loss,
      - diferença entre modos SIMULATED e REAL_MARKET_SPOT.

