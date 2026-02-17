# Laravel 12 — Convenções

- Rotas: preferir `routes/web.php` para UI e `routes/api.php` apenas se houver API real.
- Validação: usar `FormRequest` (ex: `StoreBotRequest`, `UpdateBotRequest`).
- Persistência: usar Eloquent + migrations existentes.
- Views: Blade + Bootstrap.
- Autenticação: já existe e deve ser mantida como está (não substituir por Breeze/Jetstream).
- Queries que retornam dados relacionados devem usar `->with([...])`.
- Para listas: paginação (`paginate()`).
