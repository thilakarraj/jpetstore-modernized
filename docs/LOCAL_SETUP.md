# Local Setup — Full Stack

## Prerequisites

- Python **3.11+**
- Node.js **18+**
- MySQL **8** with `jpetstore` and `jpetstore_test` (see `jpetstore-python-modernized/scripts/mysql-local-setup.sql`)

## 1. Backend

```powershell
cd D:\workspace\haiintel\jpetstore-python-modernized
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
# Edit .env: DATABASE_URL, JWT_SECRET, CORS_ORIGINS includes UI origin
alembic upgrade head
jpetstore-seed
uvicorn jpetstore.main:app --reload --host 127.0.0.1 --port 8000
```

Verify: `http://127.0.0.1:8000/health` and `http://127.0.0.1:8000/docs`

## 2. Frontend (integrated)

```powershell
cd D:\workspace\haiintel\jpetstore-ui
npm install
Copy-Item .env.example .env
# Set:
#   VITE_API_BASE_URL=http://127.0.0.1:8000
#   VITE_USE_MOCK_API=false
npm run dev
```

Open the URL Vite prints (usually `http://127.0.0.1:5173`).

## 3. Demo workflow (live API)

1. Register or sign on (`j2ee` / `j2ee` after seed on backend).
2. Browse catalog → product → select SKU → add to cart.
3. Cart → checkout → place order.
4. Order confirmation and **Order history**.

## 4. Offline UI demo (mocks only)

```powershell
# .env: VITE_USE_MOCK_API=true
npm run dev
node scripts/mock-demo-verify.mjs
```

No backend required; no database persistence.

## 5. Optional MySQL tests

```powershell
$env:TEST_DATABASE_URL="mysql+pymysql://jpetstore_app:<password>@127.0.0.1:3306/jpetstore_test?charset=utf8mb4"
pytest -m mysql -q
```

## Troubleshooting

| Issue | Action |
|-------|--------|
| CORS errors | Add UI origin to backend `CORS_ORIGINS` |
| 401 on cart/checkout | Sign on; live cart requires JWT |
| Alembic JWT error | Set `JWT_SECRET` in `.env` (32+ chars) |
| MySQL 1045 | Fix `.env` password; see deployment guide in backend repo |

More detail: `jpetstore-python-modernized/docs/DEPLOYMENT_GUIDE.md`
