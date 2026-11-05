# Integration Architecture

## System overview

| Layer | Project | Role |
|-------|---------|------|
| Reference | `jpetstore-6/` | Legacy Java/MyBatis behavior (read-only) |
| API | `jpetstore-python-modernized/` | FastAPI modular monolith, MySQL, Alembic |
| UI | `jpetstore-ui/` | React + Vite + Zustand + Axios |

Base path: **`/api/v1`**. Health: **`/health`**, **`/health/ready`**, metrics: **`/metrics`**.

## Request flow (integrated mode)

1. Browser loads `jpetstore-ui` (Vite dev or static `dist/`).
2. UI calls `VITE_API_BASE_URL` (default `http://127.0.0.1:8000`).
3. JWT on protected routes via `Authorization: Bearer`.
4. Catalog reads are public; cart and checkout require JWT (backend design).
5. Checkout uses **`POST /api/v1/orders/checkout`** with **`Idempotency-Key`**; prices and totals are computed server-side.

## Mock vs live

| Mode | Config | Behavior |
|------|--------|----------|
| Demo / offline UI | `VITE_USE_MOCK_API=true` | Fixtures in `jpetstore-ui/src/services/mocks/` |
| Integrated | `VITE_USE_MOCK_API=false` | All cart/order/catalog/auth via FastAPI |

Production must use **`VITE_USE_MOCK_API=false`**. Mock mode is opt-in only (`=== "true"`).

## CORS

Backend `CORS_ORIGINS` must include the UI origin (e.g. `http://127.0.0.1:5173`, `http://localhost:5173`).

## Contract notes vs API_SPECIFICATION.md

The assessment microservice spec describes **`POST /cart/lines`**, **`POST /orders`**, guest **`X-Cart-Id`**, and **`POST /checkout/draft`**. The implemented monolith uses:

- **`/api/v1/cart/*`** (JWT, per-user cart in MySQL)
- **`POST /api/v1/orders/checkout`** (single transactional checkout)

See `API_IMPLEMENTATION_STATUS.md` for the verified route list.

## Frontend service layout

```
jpetstore-ui/src/services/api/
  client.ts          # Axios, JWT, 401 handling
  authService.ts     # register, login, profile
  catalogService.ts  # categories, products, items, search
  cartService.ts     # cart CRUD
  orderService.ts    # checkout, order list/detail
  mappers.ts         # API DTO → UI types
```

State: **`authStore`**, **`cartStore`** (syncs cart from API after login).
