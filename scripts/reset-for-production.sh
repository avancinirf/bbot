#!/bin/bash
# Reset da base de dados e reinício com variáveis de produção.
#
# ANTES DE EXECUTAR:
# 1. Edite o .env e altere para sua conta real:
#    BINANCE_API_KEY=sua_key_real
#    BINANCE_API_SECRET=seu_secret_real
# 2. Para API de produção (não testnet), altere:
#    BINANCE_BASE_URL=https://api.binance.com
#
# Uso: ./scripts/reset-for-production.sh

set -e
cd "$(dirname "$0")/.."

echo "Limpando base de dados e cache..."
docker compose exec app php artisan db:clean --force
docker compose exec app php artisan config:clear

echo "Reiniciando o container para carregar as novas variáveis..."
docker compose restart

echo "Concluído. A aplicação está rodando com as credenciais do .env atual."
