# BBOT – API REFERENCE

Este documento lista os endpoints principais do backend do BBOT, suas entradas e saídas, além de exemplos de uso com `curl`.

A base usada nos exemplos é:

- `http://localhost:8000`

---

## Healthcheck

### GET /api/health

Retorna o estado básico do serviço.

**Resposta (200):**

```json
{
  "status": "ok",
  "service": "binance-trade-backend"
}
