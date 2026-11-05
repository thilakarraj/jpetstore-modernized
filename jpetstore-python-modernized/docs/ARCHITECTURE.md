# Architecture

Modular monolith: single FastAPI app (`jpetstore.main:app`).

## Layers

| Layer | Location |
|-------|----------|
| Operational API | `src/jpetstore/api/` |
| Business modules | `src/jpetstore/modules/` (Account, Catalog, Cart, Order) |
| Core | `src/jpetstore/core/` (database, exceptions, rate limit) |
| Security helpers | `src/jpetstore/security/` (passwords, audit) |
| Middleware | `src/jpetstore/middleware/` |
| Metrics | `src/jpetstore/metrics/` |
| Models | `src/jpetstore/models/` |

## Module map

| Phase | Package | Responsibility |
|-------|---------|----------------|
| 3 | `modules/account/` | Auth, profile, my-list |
| 4 | `modules/catalog/` | Public catalog reads |
| 5 | `modules/cart/` | Persistent JWT-scoped cart |
| 6 | `modules/order/` | Checkout, order history |

Request flow: **router → service → repository → models**.

## Middleware order (outer → inner)

CORS → Security headers → Metrics → Request logging → Request ID → routes

## JWT

Local Bearer validation on account, cart, and order routes (ADR-P3-002).
