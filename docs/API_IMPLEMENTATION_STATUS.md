# API Implementation Status

Verified against code in `jpetstore-python-modernized` (not spec alone).

## Authentication & account

| Method | Path | Status | Notes |
|--------|------|--------|-------|
| POST | `/api/v1/auth/register` | Implemented | 201; duplicate → 409 |
| POST | `/api/v1/auth/login` | Implemented | JWT bearer |
| GET | `/api/v1/account/me` | Implemented | JWT |
| PUT | `/api/v1/account/me` | Implemented | JWT |
| GET | `/api/v1/account/me/my-list` | Implemented | JWT + catalog |

## Catalog

| Method | Path | Status |
|--------|------|--------|
| GET | `/api/v1/catalog/categories` | Implemented |
| GET | `/api/v1/catalog/categories/{id}` | Implemented |
| GET | `/api/v1/catalog/categories/{id}/products` | Implemented |
| GET | `/api/v1/catalog/products/{id}` | Implemented |
| GET | `/api/v1/catalog/products/{id}/items` | Implemented |
| GET | `/api/v1/catalog/items/{id}` | Implemented |
| GET | `/api/v1/catalog/products/search` | Implemented |
| GET | `/api/v1/catalog/search` | Implemented (alias) |
| GET | `/api/v1/catalog/banners` | Implemented |

## Cart (JWT required)

| Method | Path | Status |
|--------|------|--------|
| GET | `/api/v1/cart` | Implemented |
| POST | `/api/v1/cart/items` | Implemented |
| PUT | `/api/v1/cart/items/{item_id}` | Implemented |
| DELETE | `/api/v1/cart/items/{item_id}` | Implemented |
| DELETE | `/api/v1/cart` | Implemented |

Guest **`X-Cart-Id`** carts are **not** implemented on the backend; UI requires sign-on for cart/checkout in live mode.

## Orders (JWT required)

| Method | Path | Status |
|--------|------|--------|
| POST | `/api/v1/orders/checkout` | Implemented; idempotency header |
| GET | `/api/v1/orders` | Implemented |
| GET | `/api/v1/orders/{order_id}` | Implemented |

## Not implemented (spec / legacy microservice)

| Item | Status |
|------|--------|
| `POST /checkout/draft` | Not implemented |
| `POST /orders` (separate from checkout) | Not implemented (use checkout) |
| `POST /cart/lines` | Not implemented (use `/cart/items`) |
| Internal `/internal/*` routes | Not exposed |

## Frontend wiring

| Domain | Live API when `VITE_USE_MOCK_API=false` |
|--------|----------------------------------------|
| Auth | Yes |
| Catalog | Yes |
| Cart | Yes |
| Orders | Yes |
