# Prompts prontos (Cursor)

## Prompt 0 — Boot do contexto (usar no início de cada sessão)
Use estes anexos:
@docs/CONTEXT.md
@docs/WORKPLAN.md

Tarefa:
1) Resuma o estado atual do projeto.
2) Liste próximos 3 passos do WORKPLAN em ordem.
3) Para o passo #1, proponha implementação em pequenos commits, com arquivos e comandos.

## Prompt 1 — Implementar BinanceService (fase 1)
Anexos:
@docs/CONTEXT.md
@docs/WORKPLAN.md
@app/Services/BinanceService.php (se já existir)

Implemente a Fase 1 do WORKPLAN com foco em segurança:
- Nenhum endpoint de withdraw/transfer.
- Estruture métodos: public/signed, assinatura HMAC, tratamento de erros.
Entregue:
- arquivos alterados/criados
- comandos (docker compose exec…)
- checks de validação (ex: um route/command de teste que chama ping/ticker)

## Prompt 2 — CRUD Moedas + Bots (fase 2)
Anexos:
@docs/CONTEXT.md
@routes/web.php
@app/Models/Moeda.php
@app/Models/Bot.php

Crie CRUD completo de Moeda e Bot com Blade+Bootstrap:
- FormRequests
- Controllers resource
- Views
- Eager loading obrigatório
Entregue comandos e como validar.

## Prompt 3 — Command bots:run (fase 3)
Anexos:
@docs/CONTEXT.md
@app/Models/Bot.php
@app/Models/Operacao.php

Crie `php artisan bots:run`:
- processa bots ativos
- registra Operacao
- preparado para “simulação” e “real”
Entregue comandos e testes mínimos.
