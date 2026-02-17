# WORKPLAN — Binance (Laravel 12)

## Fase 1 — BinanceService (base técnica)
- [:contentReference[oaicite:8]{index=8}nceService com:
  - [ ] client HTTP + helpers (GET/POST, signed/public)
  - [ ] assinatura HMAC SHA256 (SIGNED)
  - [ ] tratamento de erros (rate limit, time skew, erros Binance)
  - [ ] camada de DTO/arrays padronizados
- [ ] Implementar apenas endpoints necessários para TRADE (spot) e leitura de mercado
- [ ] Bloquear explicitamente qualquer endpoint de withdraw/transfer (fail-fast)

## Fase 2 — Funcionalidades do painel (CRUD + visão)
- [ ] CRUD Moedas (com status)
- [ ] CRUD Bots (relacionado a Moeda)
- [ ] Lista de Operações por Bot (com filtros e paginação)
- [ ] Dashboard (visão rápida: bots ativos, últimas operações, alertas)

## Fase 3 — Execução de Bot
- [ ] Artisan command: `bots:run` (executa bots ativos)
- [ ] Regras de idempotência (não duplicar operação)
- [ ] Registrar Operacao a cada trade/decisão
- [ ] Flags de segurança (ex: “modo simulação” vs real)

## Fase 4 — Métricas de mercado
- [ ] Coleta de preço/volume
- [ ] Indicadores (ex: médias móveis, RSI, volatilidade)
- [ ] Persistência mínima (SQLite) + cache onde fizer sentido

## Fase 5 — Qualidade e segurança
- [ ] Feature tests essenciais (CRUD + command)
- [ ] Logs estruturados (sem vazar segredos)
- [ ] Validações e políticas (authz) no painel
