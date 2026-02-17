# CONTEXTO DO PROJETO — Binance (Laravel 12)

## Objetivo
Sistema Laravel para a:contentReference[oaicite:6]{index=6}e operar trades na Binance (Spot/Exchange), com métricas e automação via bots.

## Stack
- Laravel 12 + PHP 8.4
- SQLite
- Docker: 1 container único
- UI: Bootstrap (sem Vue/React)

## Regras críticas de segurança
- Apenas Spot/Exchange API
- Proibido: withdraw/transfer/wallet endpoints
- API keys: somente permissões de TRADE (sem saques)

## Service obrigatório
- `app/Services/BinanceService.php` centraliza todas as chamadas.
- Endpoints SIGNED precisam HMAC SHA256.
- Headers e `X-MBX-APIKEY` montados dinamicamente.

## Domínio (Models)
- Moeda: id, nome (string), status (bool)
- Bot: id, nome, idmoeda (FK), valor_anterior, status enum [inativo, ativo, desabilitado, concluido] default inativo
- Operacao: id, idbot (FK), tipo enum [compra, venda], valor_anterior, valor_trade, data_trade

Relacionamentos:
- Bot pertence a Moeda
- Bot tem várias Operacoes
- Operacao representa um trade na Binance

## Execução (referência)
- Subir: `docker compose up -d --build`
- Limpar caches: `docker compose exec app php artisan optimize:clear`
- Migrar: `docker compose exec app php artisan migrate`
