# Regras do Projeto — Binance (Laravel 12 + PHP 8.4 + SQLite + Docker único)

## Contexto fixo
- Repo root: `/Users/avancini/projetos/binance`
- Stack: Laravel 12 + PHP 8.4, SQLite, 1 único container Docker.
- UI: Bootstrap (não usar Vue/React).
- Tudo deve seguir padrões do Laravel 12 (evitar receitas antigas). 

## Como responder / implementar
Sempre entregar:
1) lista objetiva do que foi criado/alterado (arquivos/classes)
2) comandos para rodar (sempre assumindo execução na raiz do repo)
3) como validar que funcionou (1-3 checks)

## Padrões
- Código simples, sem “mágica”.
- Preferir Services/Actions ao invés de lógica em Controller.
- Eager loading obrigatório quando retornar entities com relacionamentos (evitar N+1).
- Não tocar em `.env` e nunca pedir pra colar segredos em chat.
