# JPetStore Python Modernized

Modular monolith FastAPI application modernizing MyBatis JPetStore 6.

Assessment source documentation (read-only): `../docs/`

Phases **1–6** are implemented (health, schema/seed, account/JWT, catalog, cart, checkout/orders).

## Requirements

- **Python 3.11+** (developed and tested on 3.11.x)
- **MySQL 8** for development and optional integration tests
- No Docker required

## Windows local setup (PowerShell)

From the project root:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
Copy-Item .env.example .env
# Edit .env: set JWT_SECRET, DATABASE_URL, TEST_DATABASE_URL (replace <password>)
```

Create MySQL databases and user (see `scripts/mysql-local-setup.sql` and `docs/DEPLOYMENT_GUIDE.md`).

```powershell
alembic upgrade head
alembic current
jpetstore-seed
jpetstore-verify-database
pytest -q
```

Start the API:

```powershell
uvicorn jpetstore.main:app --reload --host 127.0.0.1 --port 8000
```

Verify:

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/health/ready (requires working `DATABASE_URL`)
- http://127.0.0.1:8000/metrics
- http://127.0.0.1:8000/docs

MySQL integration tests (optional):

```powershell
$env:TEST_DATABASE_URL = "mysql+pymysql://jpetstore_app:<password>@127.0.0.1:3306/jpetstore_test?charset=utf8mb4"
pytest -m mysql -q
```

## Documentation

| Doc | Purpose |
|-----|---------|
| `docs/DEPLOYMENT_GUIDE.md` | Local Windows runbook, MySQL, migrations, seed |
| `docs/TEST_STRATEGY.md` | SQLite unit tests + optional MySQL integration |
| `docs/DATABASE_DESIGN.md` | Schema and commands |
| `docs/DEV_CREDENTIALS.md` | Demo accounts (non-production) |
| `docs/LOGGING_AND_MONITORING.md` | Logs, metrics, optional Prometheus |

## Optional Prometheus

The app exposes `/metrics` without Prometheus. To scrape locally, install [Prometheus](https://prometheus.io/download/) and run:

```powershell
prometheus --config.file=monitoring/prometheus.yml
```

Open http://127.0.0.1:9090 — target `127.0.0.1:8000`.
