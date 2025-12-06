# bbot – Binance Microtrade Bot

Projeto em desenvolvimento para gerenciamento de bots de microtrade na Binance.

## Stack

- Backend: FastAPI + SQLModel + SQLite
- Integração Binance: binance-connector (Spot)
- Indicadores: pandas + numpy (EMA, RSI, MACD, ADX)
- Ambiente: Docker (tudo em um único container)

## Como subir o backend

```bash
docker compose up --build
