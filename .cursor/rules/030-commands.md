# Comandos — sempre na raiz do repo

## Docker
- Subir: `docker compose up -d --build`
- Logs: `docker compose logs -f --tail=200 app`
- Entrar: `docker compose exec app bash` (ou `sh` se não houver bash)

## Laravel (dentro do container)
- Limpar caches: `php artisan optimize:clear`
- Rebuild caches (apenas quando fizer sentido): `php artisan config:cache && php artisan route:cache && php artisan view:cache`

## Padrão para comandos do container (1 linha)
- `docker compose exec app sh -lc 'COMANDO_AQUI'`
