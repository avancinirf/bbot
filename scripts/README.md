# Scripts

## Ver seu IP para liberar na API da Binance

A Binance permite restringir a API key por IP. Para liberar o acesso:

1. No painel da Binance: **API Management** → **Restrict access to trusted IPs only** → **Add IP**.
2. Use o IP público do computador de onde a aplicação faz as requisições.

Para ver seu IP público (rode no seu computador, não dentro do Docker):

```bash
./scripts/show-my-ip.sh
```

Ou manualmente: `curl -s https://api.ipify.org`

Adicione esse IP na lista de IPs permitidos da sua API key na Binance. Se seu IP residencial mudar (reinício do roteador, etc.), será preciso adicionar o novo IP no painel.

---

## Reset para produção (limpar dados e usar conta real)

### 1. Alterar credenciais no `.env`

Edite o arquivo `.env` na raiz do projeto:

- `BINANCE_API_KEY` – API key da sua conta real
- `BINANCE_API_SECRET` – API secret da sua conta real
- Para usar a API de **produção** (não testnet), altere:
  - `BINANCE_BASE_URL=https://api.binance.com`

(Mantenha `BINANCE_BASE_URL=https://testnet.binance.vision` se ainda for usar testnet.)

**Antes de ativar a API:** libere o IP do seu computador na Binance (veja a seção “Ver seu IP” acima).

### 2. Limpar a base de dados

Remove todos os dados de **moedas**, **bots** e **operacoes** e limpa o cache (última atualização, carteira).

**Com Docker (container já rodando):**

```bash
docker compose exec app php artisan db:clean --force
docker compose exec app php artisan config:clear
docker compose restart
```

**Sem Docker (PHP local):**

```bash
php artisan db:clean --force
php artisan config:clear
# Reinicie o scheduler se estiver rodando: php artisan schedule:work
```

### 3. Script automático (Docker)

Se já tiver alterado o `.env`, pode rodar:

```bash
chmod +x scripts/reset-for-production.sh
./scripts/reset-for-production.sh
```

O script executa a limpeza, limpa o cache de configuração e reinicia o container para carregar as novas variáveis.
