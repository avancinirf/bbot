# Models do Projeto (Laravel 12) — Referência para o Gemini (VS Code)

Este arquivo descreve os models que existem (User) e os models de domínio planejados/obrigatórios (Moeda, Bot, Operacao),
com campos, relacionamentos e enums. Use isto como base para criar migrations, models, factories e validações.

⚠️ Autenticação: JÁ ESTÁ FUNCIONANDO. Não recriar scaffold de auth. O model User existe e deve ser tratado como parte da auth.

---

## 0) Convenções (Eloquent / Laravel)
- Tabelas no plural: users, moedas, bots, operacoes
- Chaves estrangeiras no padrão Laravel: moeda_id, bot_id
  - (Mesmo que o plano cite "idmoeda/idbot", use o padrão Laravel para facilitar relacionamentos.)
- Timestamps: created_at / updated_at em todas as tabelas.
- SQLite: tipos DECIMAL são aceitos, mas no SQLite viram NUMERIC; manter consistência via casts no Eloquent.

---

## 1) Model: User (já existe / auth)
**Tabela:** users

Campos típicos (Laravel):
- id (PK)
- name (string)
- email (string, unique)
- email_verified_at (datetime, nullable)
- password (string)
- remember_token (string, nullable)
- created_at / updated_at

Observações:
- Não mexer no fluxo de autenticação existente.
- Não inserir chaves/segredos aqui.

---

## 2) Model: Moeda
**Classe:** App\Models\Moeda  
**Tabela:** moedas

### Campos
- id (PK)
- nome (string) — recomendado UNIQUE
- status (boolean) — default true (ativa)
- created_at / updated_at

### Regras
- Uma Moeda pode ter vários Bots.

### Relacionamentos
- Moeda hasMany Bot

### Sugestões
- Index/unique: moedas.nome

---

## 3) Model: Bot
**Classe:** App\Models\Bot  
**Tabela:** bots

### Campos
- id (PK)
- nome (string)
- moeda_id (FK -> moedas.id)
- valor_anterior (decimal) — nullable (ou default 0)
- status (enum) — default INATIVO
- created_at / updated_at

### Regras
- Cada Bot pertence a uma Moeda.
- Um Bot tem várias Operacoes.

### Relacionamentos
- Bot belongsTo Moeda
- Bot hasMany Operacao

### Enum (status)
BotStatus:
- inativo
- ativo
- desabilitado
- concluido

### Sugestões
- Index: bots.moeda_id
- Se fizer sentido: unique (moeda_id, nome)

---

## 4) Model: Operacao
**Classe:** App\Models\Operacao  
**Tabela:** operacoes

### Campos
- id (PK)
- bot_id (FK -> bots.id)
- tipo (enum)
- valor_anterior (decimal) — nullable
- valor_trade (decimal)
- data_trade (datetime)
- created_at / updated_at

### Regras
- Cada Operacao pertence a um Bot.
- Cada Operacao representa um trade executado na Binance (Spot/Exchange).

### Relacionamentos
- Operacao belongsTo Bot

### Enum (tipo)
OperacaoTipo:
- compra
- venda

### Sugestões
- Index: operacoes.bot_id, operacoes.data_trade

---

## 5) Enums (recomendado usar PHP native enums)
Criar:
- App\Enums\BotStatus
- App\Enums\OperacaoTipo

E fazer casts no model:
- Bot: status => BotStatus::class
- Operacao: tipo => OperacaoTipo::class
- Valores decimais: casts para string/decimal conforme padrão do projeto

---

## 6) Checklist de implementação (para o Gemini executar)
1) Criar migrations: moedas, bots, operacoes (FKs e indexes).
2) Criar models com relationships + casts + fillable/guarded.
3) Criar enums.
4) Criar factories (opcional) e seeds mínimos (Moeda exemplo).
5) Criar testes básicos (migrations + relationships).
