# Segurança do projeto BBot

Este projeto foi desenhado com foco em **segurança operacional** sobre a conta da Binance.

## Escopo das operações

- O bot **NUNCA** executa:
  - saques (withdraw)
  - transferências entre contas
  - depósitos
- O bot **SOMENTE** executa:
  - consultas de dados de mercado
  - leitura de saldos
  - ordens de trade SPOT (market, por enquanto), sempre dentro da própria conta.

## Chaves da Binance

- As chaves de API são lidas **apenas via variáveis de ambiente**:
  - `BINANCE_API_KEY`
  - `BINANCE_API_SECRET`
  - `BINANCE_TESTNET=true` para usar a testnet.
- As chaves **não devem ser commitadas** no repositório.
- Recomenda-se habilitar nas permissões da chave **apenas**:
  - leitura,
  - trade spot.
- As permissões de saque devem permanecer **desativadas**.

## .env e execução local

- O arquivo `.env` é usado apenas localmente, via:
  ```bash
  docker run --rm --env-file .env ...
