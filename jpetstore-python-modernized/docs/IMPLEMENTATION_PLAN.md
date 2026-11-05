# Implementation Plan



## Phases 1–5 — Complete



Operational foundation, schema/seed, account/JWT, catalog, persistent cart.



## Phase 6 — Complete



- Checkout and order APIs (`modules/order/`)

- Migration `0004_phase6_checkout` (idempotency table + MySQL inventory check)

- Atomic checkout with idempotency, inventory decrement, sequence allocation

- Tests: `tests/test_orders.py`



## Local development (current)



- **Python 3.11+** virtual environment; `pip install -e ".[dev]"`

- **Local MySQL 8** (`jpetstore`, `jpetstore_test`); credentials in `.env`

- **No Docker** — run with `uvicorn jpetstore.main:app --reload --host 127.0.0.1 --port 8000`

- See `docs/DEPLOYMENT_GUIDE.md` and `README.md`



## Phase 7 — Pending approval



Frontend or additional scope per product owner.

