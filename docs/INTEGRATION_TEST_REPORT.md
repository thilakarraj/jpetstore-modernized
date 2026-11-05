# Integration Test Report

**Date:** 2026-11-05 (final catalog integration verification)  
**Monorepo:** `jpetstore-modernized` on branch `main`

## Automated tests executed

| Suite | Command | Result |
|-------|---------|--------|
| Backend unit + API (SQLite) | `pytest -q` in `jpetstore-python-modernized` | **118 passed**, **4 skipped** |
| Catalog API contract | `tests/test_catalog_integration_contract.py` | **Included in pytest run** |
| MySQL integration | `pytest -m mysql` | **Not run** (requires `TEST_DATABASE_URL`) |
| DB verify (MySQL) | `jpetstore-verify-database` | **OK** when run from `haiintel/jpetstore-python-modernized` with valid `.env`; **1045** if `.env` password wrong (monorepo copy has no local `.env`) |
| Frontend lint | `npm run lint` | **Pass** (1 pre-existing warning in `ThemeProvider.tsx`) |
| Frontend build | `npm run build` | **Pass** |

## Live HTTP API (running uvicorn on `:8000`)

Verified with `Invoke-RestMethod` / HTTP client:

| Endpoint | Result |
|----------|--------|
| `GET /api/v1/catalog/categories` | **5** categories |
| `GET /api/v1/catalog/categories/FISH` | **200** |
| `GET /api/v1/catalog/categories/FISH/products` | **4** products |
| `GET /api/v1/catalog/products/FI-SW-01` | **Angelfish** |
| `GET /api/v1/catalog/products/FI-SW-01/items` | **2** items |
| `GET /api/v1/catalog/items/EST-1` | **quantity 10000** |
| `GET /api/v1/catalog/products/search?keyword=fish` | **2** products |

## Browser verification

| Check | Result |
|-------|--------|
| Playwright `scripts/live-catalog-verify.mjs` | **Not passing in this run** — no `/api/v1/catalog/*` XHR observed against `:8000` while Vite was up (likely dev env still on mock or CORS origin mismatch: use `http://localhost:5173` until backend `CORS_ORIGINS` includes `http://127.0.0.1:5173`) |
| Manual | See `docs/LOCAL_SETUP.md` — set `VITE_USE_MOCK_API=false`, align CORS, open DevTools Network |

## Catalog integration behavior (live mode)

- `VITE_USE_MOCK_API` must be exactly `false` for live FastAPI catalog.
- `VITE_API_BASE_URL` normalized (no trailing slash); dev console logs mode/base URL.
- Optional `VITE_USE_DEV_PROXY=true` proxies `/api` only (empty base URL).
- Home/Catalog/Category/Product pages show loading, empty, and error states with retry.
- Product cards load item prices from `GET .../products/{id}/items` in live mode.

## Known limitations

- Guest cart / cart merge not implemented on backend.
- Live cart/checkout require JWT sign-on.
- MySQL-marked tests optional.
- Backend `.env` must list **both** `http://localhost:5173` and `http://127.0.0.1:5173` in `CORS_ORIGINS` (see `.env.example`).

## How to re-run

```powershell
# Backend (monorepo)
cd D:\workspace\haiintel\jpetstore-modernized\jpetstore-python-modernized
.\.venv\Scripts\Activate.ps1
pytest -q

# Frontend
cd D:\workspace\haiintel\jpetstore-modernized\jpetstore-ui
npm run lint
npm run build

# Live browser smoke (backend :8000, UI :5173, mock off)
cd jpetstore-ui
# Copy .env.example -> .env, set VITE_USE_MOCK_API=false
npm run dev
node scripts/live-catalog-verify.mjs
```
