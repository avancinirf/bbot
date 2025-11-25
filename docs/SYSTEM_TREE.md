# BBOT – SYSTEM TREE

Este documento apresenta uma visão geral da estrutura de diretórios do projeto.

A estrutura exata pode variar ligeiramente, mas a organização geral é a seguinte.

---

## Estrutura geral

```text
.
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── binance_client.py
│   ├── indicators.py
│   ├── bot_engine.py
│   ├── bot_risk.py
│   ├── bot_rebalance.py
│   ├── routes_bots.py
│   ├── routes_bot_assets.py
│   ├── routes_bot_analysis.py
│   ├── routes_trade_logs.py
│   ├── routes_bot_trade.py
│   ├── routes_bot_simtrade.py
│   ├── routes_bot_rebalance.py
│   └── config.py (se existir)
│
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       └── components/
│           ├── BotsList.jsx
│           ├── ActiveBotPanel.jsx
│           ├── ActiveBotAssets.jsx
│           ├── ActiveBotMarketStatus.jsx
│           ├── ActiveBotOpportunity.jsx
│           ├── ActiveBotLogs.jsx
│           └── FooterInfo.jsx
│
├── data/
│   └── bot.db
│
├── docs/
│   ├── OVERVIEW.md
│   ├── PROJECT_SCOPE.md
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── BACKEND_MODULES.md
│   ├── FRONTEND.md
│   ├── BACKLOG.md
│   ├── SETUP.md
│   ├── CONTRIBUTING.md
│   └── SYSTEM_TREE.md
│
├── .env
├── .gitignore
├── .dockerignore
└── Dockerfile
