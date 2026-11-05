# Deployment Guide (local Windows)

This project runs **directly on Windows** with Python and a local **MySQL 8** instance. Docker is not required.

## 1. Prerequisites

| Component | Notes |
|-----------|--------|
| Python | **3.11+** (`python --version`) |
| MySQL | **8.x**, utf8mb4 / utf8mb4_unicode_ci |
| Git | Optional |

Confirm MySQL is listening (default port **3306**; yours may differ):

```powershell
Test-NetConnection -ComputerName 127.0.0.1 -Port 3306
```

## 2. Python environment

```powershell
cd D:\workspace\haiintel\jpetstore-python-modernized
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## 3. Environment file

```powershell
Copy-Item .env.example .env
```

Edit `.env` (copy from `.env.example` if missing). **`JWT_SECRET`** has a local-dev default in code; you must still set **`DATABASE_URL`** (and MySQL password) in `.env` for a working database.

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Dev DB **`jpetstore`**, user **`jpetstore_app`** |
| `TEST_DATABASE_URL` | Integration tests → **`jpetstore_test` only** |
| `JWT_SECRET` | At least 32 characters |
| `APP_ENV` | `development` for local work |
| `LOG_DIR` | e.g. `./logs` (Windows path OK) |

Example shape (replace `<password>` and port if needed):

```env
DATABASE_URL=mysql+pymysql://jpetstore_app:<password>@127.0.0.1:3306/jpetstore?charset=utf8mb4
TEST_DATABASE_URL=mysql+pymysql://jpetstore_app:<password>@127.0.0.1:3306/jpetstore_test?charset=utf8mb4
APP_ENV=development
```

Load env for Alembic and CLI (PowerShell):

```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), 'Process')
  }
}
```

If `alembic` fails with **1045 Access denied** but `.env` looks correct, a stale **`DATABASE_URL` in your shell** may override `.env`. Clear it and retry:

```powershell
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:TEST_DATABASE_URL -ErrorAction SilentlyContinue
```

Or open a **new PowerShell window** after editing `.env`.

**Do not leave `<password>` in `.env`** — replace it with the real MySQL password for `jpetstore_app` (same value as in `scripts/mysql-local-setup.sql`).

## 4. MySQL setup

Run as a MySQL administrator. Template: **`scripts/mysql-local-setup.sql`** (replace `<password>`).

Creates:

- Database **`jpetstore`** (development)
- Database **`jpetstore_test`** (integration tests)
- User **`jpetstore_app`** with grants on both

**Never** point `TEST_DATABASE_URL` at `jpetstore` for destructive integration tests.

## 5. Migrations

```powershell
alembic upgrade head
alembic current
```

Expected revisions through Phase 6: `0001` … `0004_phase6_checkout`.

Do **not** run `alembic downgrade` on shared databases automatically.

## 6. Seed (development / test only)

```powershell
jpetstore-seed
```

Refuses when `APP_ENV=production`. Idempotent — safe to run repeatedly.

Demo users: `docs/DEV_CREDENTIALS.md`.

## 7. Verify database

Ping dev connection (`DATABASE_URL`):

```powershell
jpetstore-verify-database
```

Migrate + seed idempotency on test DB (`TEST_DATABASE_URL` → `jpetstore_test`):

```powershell
jpetstore-verify-database --integration
```

## 8. Run the application

```powershell
uvicorn jpetstore.main:app --reload --host 127.0.0.1 --port 8000
```

| URL | Expected |
|-----|----------|
| `/health` | 200, liveness |
| `/health/ready` | 200 when MySQL up; 503 if DB down |
| `/metrics` | Prometheus text |
| `/docs` | OpenAPI UI |

## 9. Tests

```powershell
pytest -q
pytest -m mysql -q   # only when TEST_DATABASE_URL is valid
```

## 10. Optional Prometheus

Not required for startup. With the app on port 8000:

1. Download Prometheus for Windows from https://prometheus.io/download/
2. Run: `prometheus --config.file=monitoring/prometheus.yml`
3. UI: http://127.0.0.1:9090 (scrapes `127.0.0.1:8000`)

See `docs/LOGGING_AND_MONITORING.md` for log files under `LOG_DIR`.
