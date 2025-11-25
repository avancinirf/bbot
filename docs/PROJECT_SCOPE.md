# BBOT – PROJECT SCOPE

Este documento descreve o escopo conceitual do BBOT, os objetivos do projeto, suas restrições e princípios fundamentais. Ele serve como referência para desenvolvedores humanos e para sistemas de IA que venham a dar continuidade ao desenvolvimento.

---

## Objetivo geral

Criar um bot de micro trade para a Binance que:

- opere em ambiente local, containerizado, com todos os serviços em um único Docker;
- use a API da Binance (preferencialmente testnet durante desenvolvimento);
- seja focado exclusivamente em operações de trade dentro da conta (SPOT);
- nunca realize saques, depósitos, transferências ou operações fora de SPOT;
- seja simples de operar, com interface clara, permitindo:
  - criação de bots;
  - configuração de moedas;
  - ajuste de parâmetros de trade;
  - ativação/desativação e rebalanceamento.

---

## Princípios fundamentais

1. **Somente trade, nunca saque ou depósito**

   O sistema não deve, em nenhuma hipótese, implementar lógica para:
   - saque de fundos;
   - depósito de fundos;
   - transferências ou envio para terceiros;
   - operações de margem ou futuros.

   Somente é permitido:
   - compra e venda de moedas dentro da conta própria, via SPOT.

2. **Apenas um bot ativo por vez**

   Embora o sistema suporte múltiplos bots, por simplicidade e segurança:
   - apenas um bot pode estar ativo em determinado momento;
   - ativar um bot implica desativar os demais.

3. **Modo simulado como padrão**

   Todo bot deve começar (ou poder ser mantido) em modo:
   - `SIMULATED` – onde nenhuma ordem é enviada à Binance.

   O modo:
   - `REAL_MARKET_SPOT` (envio de ordens reais) deve ser opcional e sempre explícito.

4. **Valor padrão de trade: 10 USDT**

   O conceito de “trade unit” é central:
   - inicialmente, todas as operações são baseadas em um valor de referência de 10 USDT;
   - a quantidade de uma moeda é calculada como:
     - `quantidade = 10 USDT / preço atual da moeda`.

   Futuramente, cada bot e/ou cada moeda poderá ter um valor próprio configurável, mas o padrão atual é global.

5. **Trade baseado em variação percentual**

   Cada moeda tem:
   - preço inicial em USDT;
   - percentual de gatilho para compra (`buy_percent`, ex.: -3%, -5%);
   - percentual de gatilho para venda (`sell_percent`, ex.: +3%, +5%).

   Regras:
   - compra apenas quando o preço atual estiver abaixo do inicial pelo valor de `buy_percent`;
   - venda apenas quando o preço atual estiver acima do inicial pelo valor de `sell_percent`.

   Valores de `buy_percent` e `sell_percent` devem ser livres, permitindo até 0.5%, 1%, 2%, 5% ou valores maiores para cenários específicos (por exemplo, 120%).

6. **Trades via USDT como referência**

   Todas as moedas são avaliadas em relação a USDT:

   - USDT é a moeda de referência;
   - trocas entre duas moedas (ex.: ETH ↔ BTC) devem, conceitualmente, ser modeladas via USDT:
     - vender ETH → obter USDT;
     - comprar BTC → usando USDT.

   Isso simplifica a lógica e garante consistência com as cotações.

7. **Saldo virtual por bot**

   Cada bot tem um “saldo virtual” em USDT, usado para:

   - limitar o quanto do saldo real da conta está “dedicado” àquele bot;
   - controlar perdas e acionar stop-loss;
   - calcular rebalanceamento.

   Além disso:
   - cada moeda tem uma quantidade reservada, equivalente a ~10 USDT;
   - excedentes podem ser tratados como saldo adicional do bot e usados em rebalanceamentos futuros.

8. **Stop-loss por bot**

   Cada bot possui:
   - `initial_balance_usdt` – valor virtual inicial;
   - `current_balance_usdt` – valor virtual atual;
   - `stop_loss_percent` – parâmetro de stop-loss (ex.: 40%).

   Quando a perda relativa ultrapassa o `stop_loss_percent`, o bot:
   - entra em modo de parada (STOP);
   - pode (dependendo da configuração) apenas parar ou realizar ações adicionais;
   - deve ser desativado (`is_active = false`).

---

## Escopo funcional

### Bots

- criar bot com:
  - nome;
  - saldo inicial (USDT);
  - saldo atual (USDT, inicialmente igual ao saldo inicial);
  - stop-loss em percentual;
  - modo de trade (`SIMULATED` ou `REAL_MARKET_SPOT`).

- ativar/desativar bot:
  - garantir que apenas um bot fique ativo.

- atualizar parâmetros:
  - saldo inicial (somente se fizer sentido na estratégia);
  - stop-loss;
  - modo de trade.

### Moedas (Assets)

Para cada bot:

- adicionar moedas com:
  - símbolo (ex.: `ETH`);
  - percentuais de compra e venda (com alguns defaults sugeridos, ex.: -3% e +5%);
  - flags de “pode comprar” e “pode vender”.

- atualizar configurações de uma moeda:
  - ajustes finos de `buy_percent` e `sell_percent`;
  - ativar/desativar compra/venda.

- remover moedas:
  - somente se o bot estiver desativado.

### Análise e indicadores

- obter preço atual das moedas (via Binance);
- calcular:
  - variação em relação ao preço inicial;
  - RSI(14);
  - EMAs;
  - tendência.

- retornar:
  - estado atual de cada moeda;
  - classificação em “zona de compra” ou “zona de venda”.

### Oportunidade de trade

- identificar par (venda, compra) ideal:
  - moeda A em zona de venda;
  - moeda B em zona de compra;
  - negociar em torno de 10 USDT por operação (valor padrão);
  - preferir pares com maior diferença percentual combinada.

- expor essa sugestão via API e UI:
  - sem executar automaticamente (a princípio);
  - com possibilidade futura de execução automática via engine.

### Execução de trade

Modo simulado:

- calcular trade usando preços atuais;
- atualizar saldos virtuais do bot e das moedas;
- atualizar preços iniciais das moedas envolvidas;
- registrar log.

Modo real:

- calcular quantidades com base em 10 USDT;
- ajustar às regras da Binance (LOT_SIZE, MIN_NOTIONAL);
- enviar ordens MARKET via API;
- atualizar saldos internos do bot;
- registrar log.

### Rebalanceamento

- objetivo: manter ~10 USDT por moeda no bot;
- utilizar:
  - USDT disponível;
  - excedente de moedas (convertido virtualmente a USDT);
- caso não haja saldo suficiente:
  - realizar compras parciais;
  - marcar que o último rebalance foi insuficiente.

---

## Escopo não funcional

- ambiente de desenvolvimento e execução local (MacBook Pro M1);
- container Docker único para todo o sistema (backend + build do frontend + DB SQLite via volume);
- uso de `.env` para configuração de:
  - chaves Binance (testnet / produção);
  - intervalos de engine;
  - flags de testnet.

---

## Fora de escopo (por enquanto)

- suporte a futuros, margem ou derivativos;
- múltiplos bots ativos simultaneamente;
- execução de ordens LIMIT, OCO, etc.;
- estratégias avançadas de IA para tomada de decisão (além de indicadores simples);
- dashboards complexos com gráficos históricos e estatísticas avançadas;
- orquestração com múltiplos containers ou serviços externos.

---

## Uso futuro deste documento

Este documento deve ser utilizado como referência principal para:

- validar se novas funcionalidades respeitam as regras fundamentais;
- orientar IAs ou novos desenvolvedores na compreensão do propósito do BBOT;
- decidir se uma mudança de arquitetura está alinhada com o objetivo do projeto;
- servir como contrato de escopo entre o comportamento atual e o esperado.
