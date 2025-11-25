# Roadmap – bbot

## 1. Backend

### Já implementado
- [x] CRUD completo de bots e assets.
- [x] Modo SIMULATED vs REAL_MARKET_SPOT.
- [x] Integração Binance testnet.
- [x] Endpoint de análise, indicadores e oportunidade.
- [x] Simulação de swap via USDT.
- [x] Market swap real via Binance.
- [x] Rebalance manual com alvo ~10 USDT por ativo.
- [x] Stop-loss de bot (ex.: 40%).

### Pendente / desejável
- [ ] Motor automático:
  - loop contínuo para:
    - checar oportunidade,
    - executar trade (simulado ou real),
    - respeitar intervalo `BOT_ENGINE_INTERVAL_SECONDS`.
- [ ] Regras mais avançadas de risco:
  - opção de “vender tudo” no stop-loss ou apenas parar.
- [ ] Configuração individual de:
  - valor de trade por ativo (hoje 10 USDT geral).
- [ ] WebSocket:
  - streaming de:
    - preços,
    - oportunidades,
    - logs.

## 2. Frontend

### Já implementado
- [x] Dashboard com bot ativo + lista de bots.
- [x] Painel de ativos com variação e flags de buy/sell.
- [x] Exibição de indicadores (RSI, EMA, tendência).
- [x] Exibição de logs.

### Pendente
- [ ] Form de criação de bot (sem usar `curl`).
- [ ] Form de adição/remoção de moedas:
  - bloqueado quando bot estiver ativo.
- [ ] Editar buy/sell percent diretamente via UI.
- [ ] Botão de rebalance no painel.
- [ ] Controle de modo SIMULATED/REAL na UI (visual bem destacado).

## 3. Infra / DevX

- [x] Docker único com backend + build do frontend.
- [x] `.env` com configs sensíveis.
- [ ] Documentar melhor:
  - variáveis de ambiente,
  - processo de deploy em outra máquina (ainda que local).
- [ ] Ajustar `.gitignore` pra não subir `data/bot.db` se desejar.
