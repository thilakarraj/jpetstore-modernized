# Test Strategy



```bash

pip install -e ".[dev]"

pytest -q

```



## Layers



| Layer | Database | How |

|-------|----------|-----|

| Unit / API tests | In-memory SQLite (`sqlite+pysqlite:///:memory:`) | Default `pytest`; FK enforcement via `PRAGMA foreign_keys=ON` |

| MySQL integration | **`jpetstore_test` only** | Set `TEST_DATABASE_URL`; run `pytest -m mysql` |

| MySQL concurrency | MySQL 8 + `jpetstore_test` | `tests/test_mysql_concurrency.py` (row locks / `FOR UPDATE`) |



Integration tests **refuse** to run if `TEST_DATABASE_URL` is unset or if the database name is not `jpetstore_test`. They must **never** target the development database `jpetstore`.



Example:



```powershell

$env:TEST_DATABASE_URL="mysql+pymysql://jpetstore_app:jpetstore@127.0.0.1:3307/jpetstore_test?charset=utf8mb4"

pytest -m mysql -q

```



Optional verification without pytest:



```bash

jpetstore-verify-database --integration

```



## Fixtures



- `client` — operational endpoints (default SQLite engine from app lifespan)

- `api_client` — full schema on shared in-memory SQLite (`StaticPool`) for HTTP account tests

- `db_session` / `db_engine` — isolated ORM tests with FK enforcement



## Phase 1



`test_health.py`, `test_logging.py`, `test_metrics.py`, `test_log_rotation.py`, etc.



## Phase 2



- `test_models.py` — FK, PK, constraints

- `test_passwords.py` — SEC-T-001

- `test_seed.py` — idempotency, production guard

- `test_alembic.py` — upgrade/downgrade on isolated SQLite file

- `test_database_transaction.py` — rollback



## Phase 3



`test_account_auth.py` — registration, login, JWT, authorization, rate limits, audit redaction.



## Phase 4



`test_catalog.py` — categories, products, items, inventory, search, pagination, banners, my-list auth, legacy seed parity.



Use `catalog_client` fixture (full legacy catalog seed on isolated SQLite).



## Phase 5



`test_cart.py` — add/update/remove/clear, JWT, ownership, pricing, persistence, concurrency, rollback.  

Shared seed: `tests/seed_helpers.py`.



## Phase 6



`test_orders.py` — checkout, idempotency, inventory, ownership, payment minimization, cart lifecycle.  

Row-level locking semantics for checkout sequences are partially covered on SQLite; MySQL behavior is covered by `test_mysql_concurrency.py` when `TEST_DATABASE_URL` is set.



## MySQL integration module



- `tests/test_mysql_integration.py` — connection, `alembic upgrade head`, seed idempotency on MySQL

- `tests/test_mysql_concurrency.py` — concurrent sequence allocation (MySQL 8)



## Environment



Tests set `APP_ENV=test`, in-memory `DATABASE_URL`, and a test `JWT_SECRET` in `tests/conftest.py` unless overridden by MySQL markers/fixtures.



Do not report MySQL validation as passed unless `pytest -m mysql` (or `jpetstore-verify-database --integration`) was executed successfully against a live MySQL 8 instance.

Docker is not used; run the app and MySQL directly on the host (see `docs/DEPLOYMENT_GUIDE.md`).




