# JPetStore Modernization

AI-native modernization of the classic [MyBatis JPetStore 6](https://github.com/mybatis/jpetstore-6) pet store demo into a production-oriented full stack: **Python FastAPI** backend, **React TypeScript** frontend, and **MySQL** persistence with automated tests and integration documentation.

The original Java reference application is not included in this repository; it remains a separate legacy baseline for behavior and schema comparison.

## Architecture overview

```text
┌─────────────────┐     HTTPS/JSON      ┌──────────────────────────┐
│  jpetstore-ui   │ ◄──────────────────► │ jpetstore-python-        │
│  React + Vite   │   /api/v1/* + JWT    │ modernized (FastAPI)     │
└─────────────────┘                      └────────────┬─────────────┘
                                                      │
                                                      ▼
                                            MySQL 8 (jpetstore)
```

- **Modular monolith** backend with SQLAlchemy models, Alembic migrations, JWT auth, catalog, authenticated cart, checkout, and order history.
- **SPA frontend** with responsive layout, dark/light theme, Zustand state, and optional mock API mode for UI-only demos.
- **Shared docs** at `docs/` describe API contracts, integration architecture, database design, and local setup.

## Technology stack

| Layer | Technologies |
|-------|----------------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2, Alembic, PyMySQL, Pydantic, pytest |
| Frontend | React 18, Vite 6, TypeScript, Tailwind CSS, Framer Motion, Zustand, Axios, React Hook Form, Zod |
| Database | MySQL 8 (`jpetstore` dev, `jpetstore_test` for optional integration tests) |

## Repository structure

```text
jpetstore-modernized/
├── jpetstore-ui/                 # React storefront
├── jpetstore-python-modernized/  # FastAPI API and tests
├── docs/                         # API spec, integration, local setup
├── .gitignore
└── README.md
```

## Local setup

**Prerequisites:** Python 3.11+, Node.js 18+, MySQL 8.

See **`docs/LOCAL_SETUP.md`** for step-by-step instructions. Summary:

### Backend

```powershell
cd jpetstore-python-modernized
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
# Edit JWT_SECRET, DATABASE_URL, CORS_ORIGINS (include UI origin)
alembic upgrade head
jpetstore-seed
uvicorn jpetstore.main:app --reload --host 127.0.0.1 --port 8000
```

Health: `http://127.0.0.1:8000/health` · OpenAPI: `http://127.0.0.1:8000/docs`

### Frontend

```powershell
cd jpetstore-ui
npm install
Copy-Item .env.example .env
# VITE_API_BASE_URL=http://127.0.0.1:8000
# VITE_USE_MOCK_API=false
npm run dev
```

### Environment variables

| Location | Key variables |
|----------|----------------|
| Backend `.env` (from `.env.example`) | `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`, optional `TEST_DATABASE_URL` |
| Frontend `.env` | `VITE_API_BASE_URL`, `VITE_USE_MOCK_API` |

Never commit real `.env` files or production secrets.

### Database migrations and seed

From `jpetstore-python-modernized`:

```powershell
alembic upgrade head
jpetstore-seed
```

MySQL bootstrap SQL: `jpetstore-python-modernized/scripts/mysql-local-setup.sql`.

## API documentation

- Contract and endpoint details: [`docs/API_SPECIFICATION.md`](docs/API_SPECIFICATION.md)
- Implementation status vs spec: [`docs/API_IMPLEMENTATION_STATUS.md`](docs/API_IMPLEMENTATION_STATUS.md)
- Live OpenAPI when the API is running: `/docs` and `/redoc`

## Testing

**Backend** (from `jpetstore-python-modernized`, venv active):

```powershell
pytest -q
pytest -m mysql -q   # optional; requires TEST_DATABASE_URL and MySQL
```

**Frontend:**

```powershell
cd jpetstore-ui
npm run lint
npm run build
```

Integration notes and reports: [`docs/INTEGRATION_TEST_REPORT.md`](docs/INTEGRATION_TEST_REPORT.md).

## Theme (UI)

Dark mode is the default. The header theme toggle (desktop and mobile) persists preference in `localStorage` under `jpetstore-theme`. Design tokens live under `jpetstore-ui/src/styles/`.

## Integration status

With `VITE_USE_MOCK_API=false` and a running backend, the UI uses live APIs for **auth**, **account profile**, **catalog**, **cart** (JWT required), **checkout**, and **order history** where implemented on the server.

**Mock-only mode** (`VITE_USE_MOCK_API=true`) runs without a backend for catalog/cart/order fixtures; useful for UI demos (`jpetstore-ui/scripts/mock-demo-verify.mjs`).

## Known limitations

- **Guest cart** and **cart merge on login** are not implemented on the backend; live shopping cart and checkout require sign-on.
- Some paths differ from the aspirational monolith spec (e.g. cart items under `/api/v1/cart/items`, checkout via `POST /api/v1/orders/checkout` rather than separate draft-order flows). See `docs/API_IMPLEMENTATION_STATUS.md`.
- **MySQL-marked pytest** (`pytest -m mysql`) is optional and blocked without valid `TEST_DATABASE_URL` credentials.
- Strict byte-for-byte compatibility with the original Java JPetStore URLs and session behavior is not a goal of this modernization.

## Further reading

| Document | Purpose |
|----------|---------|
| [`docs/LOCAL_SETUP.md`](docs/LOCAL_SETUP.md) | Full-stack local run |
| [`docs/INTEGRATION_ARCHITECTURE.md`](docs/INTEGRATION_ARCHITECTURE.md) | Frontend–backend wiring |
| [`docs/DATABASE_DESIGN.md`](docs/DATABASE_DESIGN.md) | Schema overview |
| `jpetstore-python-modernized/docs/DEPLOYMENT_GUIDE.md` | Backend runbook |
| `jpetstore-python-modernized/docs/TEST_STRATEGY.md` | Test layers |
