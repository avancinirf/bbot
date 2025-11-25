# BBOT – OVERVIEW

BBOT (Binance Bot) é um sistema de micro trade automatizado para a Binance, focado em operações simples, seguras e controladas localmente.

O objetivo principal é permitir a criação de bots de trade que:
- operem apenas em SPOT (sem futuros, margem ou derivativos);
- nunca executem saques, depósitos ou transferências – apenas conversões entre moedas;
- funcionem inicialmente em modo SIMULATED e só operem em modo REAL mediante configuração explícita;
- utilizem um valor padrão de trade (hoje 10 USDT) por operação, com planejamento para flexibilizar esse valor por moeda e por bot.

A aplicação é composta por:
- backend (FastAPI + SQLModel + SQLite + integração com Binance);
- frontend (React + Vite, uma SPA simples);
- engine de bot (lógica de análise, oportunidade, rebalance e execução de trade);
- empacotamento em um único container Docker, rodando em ambiente local (MacBook Pro M1 ou similar).

---

## Principais conceitos

### Bot

Um bot representa uma “carteira lógica” dentro da conta Binance do usuário. Ele trabalha com:

- saldo inicial em USDT (valor virtual reservado ao bot);
- saldo atual em USDT, atualizado conforme operações;
- um conjunto de moedas (assets) monitoradas;
- um modo de operação: 
  - `SIMULATED`: operações apenas virtuais;
  - `REAL_MARKET_SPOT`: operações reais na Binance (ordens MARKET SPOT);
- uma regra de stop-loss, definida em percentual de perda sobre o valor inicial do bot;
- um estado de atividade: apenas um bot pode estar ativo por vez.

### Asset (moeda do bot)

Cada bot possui uma lista de moedas que ele acompanha e negocia. Para cada moeda:

- símbolo (ex.: `ETH`, `BTC`, `SOL`, `XRP`);
- preço inicial em USDT, usado como referência;
- quantidade reservada da moeda, equivalente a ~10 USDT (valor padrão atual);
- percentuais de compra e venda:
  - `buy_percent` (ex.: -3%, -5%);
  - `sell_percent` (ex.: +3%, +5%);
- flags indicando se a moeda está habilitada para compra ou venda.

Esses parâmetros definem quando uma moeda entra em “zona de compra” ou “zona de venda”.

### Indicadores de mercado

Para cada moeda o sistema obtém dados da Binance e calcula:

- preço atual em USDT;
- variação percentual em relação ao preço inicial;
- RSI (14 períodos);
- EMA rápida;
- EMA lenta;
- tendência simples (ex.: UP/DOWN).

Esses indicadores servem como insumo para analisar se há oportunidade de trade.

### Oportunidade de trade

O bot analisa todas as moedas do seu portfólio, classificando-as em:

- moedas em zona de venda (acima do `sell_percent`);
- moedas em zona de compra (abaixo do `buy_percent`).

Quando há pelo menos uma moeda em zona de venda e uma em zona de compra, o sistema sugere um par:

- vender moeda A (sobrevalorizada em relação ao seu preço inicial);
- comprar moeda B (subvalorizada em relação ao seu preço inicial).

Essa sugestão é exposta via API e via interface.

---

## Modos de operação

### Modo SIMULATED

- Nenhuma ordem é enviada à Binance.
- As operações são simuladas usando dados de preço de mercado.
- Os saldos das moedas e o saldo em USDT do bot são ajustados virtualmente.
- Logs de trade são gravados com um tipo específico (ex.: `SIMULATED_SWAP`).

Este modo é o padrão e deve ser usado para testes, validação de estratégias e desenvolvimento.

### Modo REAL_MARKET_SPOT

- O sistema envia ordens reais do tipo MARKET para a Binance (SPOT).
- A integração deve usar sempre chaves de API com permissão apenas de trade (sem saque).
- As quantidades negociadas são ajustadas de acordo com os filtros da Binance (LOT_SIZE, MIN_NOTIONAL).
- Logs de trade registram esses eventos como operações reais.

---

## Segurança e restrições

Regras que devem ser respeitadas por qualquer evolução do sistema:

1. O bot nunca deve executar operações de:
   - saque;
   - depósito;
   - transferência entre contas;
   - operações de margem ou futuros.

2. Apenas ordens SPOT são permitidas, preferencialmente:
   - tipo MARKET;
   - via pares `XXXUSDT`.

3. Toda lógica de trade real deve passar por:
   - validação de filtros (LOT_SIZE, MIN_NOTIONAL);
   - logs completos.

4. O sistema deve sempre permitir operar em modo SIMULATED, mesmo que o modo REAL exista.

---

## Componentes principais

- Backend:
  - FastAPI para APIs REST;
  - SQLModel e SQLite para persistência;
  - integração com API da Binance para preços, klines e ordens;
  - módulos separados para risco, rebalance, análise e trade.

- Frontend:
  - React + Vite;
  - página única com:
    - lista de bots;
    - painel do bot ativo;
    - lista de moedas e status;
    - indicadores;
    - logs de trade.

- Docker:
  - imagem única que:
    - instala dependências Python;
    - instala e builda o frontend;
    - inicia o backend servindo a SPA e as APIs;
    - monta o volume de dados para o arquivo SQLite.

---

## Estado atual do projeto

- Backend funcional para:
  - criação e ativação de bots;
  - gerenciamento de moedas do bot;
  - análise de mercado e cálculo de indicadores;
  - sugestão de oportunidades;
  - simulação de trade;
  - execução real de trade MARKET SPOT;
  - rebalanceamento;
  - registro de logs.

- Frontend funcional para:
  - exibir bot ativo;
  - listar moedas e variação;
  - exibir indicadores e oportunidades;
  - visualizar logs.

- Infraestrutura:
  - Docker único configurado;
  - uso de `.env` para configurar chaves da Binance e parâmetros de engine.

A evolução do projeto deve seguir o escopo descrito em `PROJECT_SCOPE.md` e o planejamento registrado em `BACKLOG.md`.
