#!/bin/bash
# Mostra o IP público do seu computador para liberar no painel da API da Binance.
# Binance > API Management > Restrict access to trusted IPs only > Add IP.
echo "Seu IP público (use este IP para liberar na API da Binance):"
curl -s --max-time 5 https://api.ipify.org || curl -s --max-time 5 https://ifconfig.me/ip || echo "Não foi possível obter o IP. Verifique sua conexão."
