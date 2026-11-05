# Integration Test Report

**Date:** 2025-11-05 (local run)  
**Backend:** `jpetstore-python-modernized` Python 3.11  
**Frontend build:** `jpetstore-ui` Vite 6 — **pass**

## Automated tests executed

| Suite | Command | Result |
|-------|---------|--------|
| Backend unit + API (SQLite) | `pytest -q` (excluding optional MySQL markers) | **116 passed** |
| Shopping integration flow | `pytest tests/test_shopping_integration_flow.py -q` | **1 passed** |
| MySQL integration | `pytest -m mysql` | **Not run** (requires `TEST_DATABASE_URL` + MySQL) |
| Frontend production build | `npm run build` | **Pass** |
| UI mock demo (optional) | `node scripts/mock-demo-verify.mjs` with `VITE_USE_MOCK_API=true` | Previously **pass** (63 checks) |

## `test_shopping_integration_flow` coverage

- Register + duplicate register (409)
- Invalid login (401)
- Login + JWT
- Categories + search + product items
- Add to cart, get cart
- Checkout with idempotency key
- Order list + detail
- Unauthorized order access (401)

## Not verified in this run

- Full browser E2E against live MySQL (requires DB credentials + both servers running)
- Guest cart / cart merge (backend not implemented)
- Expired JWT edge case (manual or dedicated test)
- Concurrent checkout on MySQL (see `test_mysql_concurrency.py` when MySQL available)

## How to re-run

```powershell
# Backend
cd D:\workspace\haiintel\jpetstore-python-modernized
.\.venv\Scripts\Activate.ps1
pytest -q

# Frontend
cd D:\workspace\haiintel\jpetstore-ui
npm run build
```
