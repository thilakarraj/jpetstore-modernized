# Database Design (integration view)

Authoritative detail: `jpetstore-python-modernized/docs/DATABASE_DESIGN.md`.

## Databases (local)

| Database | Purpose |
|----------|---------|
| `jpetstore` | Development / integrated runtime |
| `jpetstore_test` | Automated MySQL tests only |

User: **`jpetstore_app`**. Charset: **utf8mb4** / **utf8mb4_unicode_ci**.

## Schema source

- Alembic revisions **`0001` … `0004_phase6_checkout`**
- Legacy table names preserved (Phase 2)
- **`cart`**, **`cart_item`** (Phase 5)
- **`checkout_idempotency`**, inventory CHECK (Phase 6)

## Transaction boundaries

- **Cart** mutations: commit per request; rollback on error.
- **Checkout**: single transaction — order, line items, inventory decrement, cart completion, idempotency record.

## Setup

See `LOCAL_SETUP.md` and `jpetstore-python-modernized/scripts/mysql-local-setup.sql`.

Do not drop or reset shared databases without explicit approval.
