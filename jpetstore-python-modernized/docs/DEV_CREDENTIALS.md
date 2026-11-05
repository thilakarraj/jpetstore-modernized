# Development credentials (non-production only)

**Do not use in production.** These mirror legacy JPetStore demo accounts for local testing only.

| Username | Password (dev) | Notes |
|----------|----------------|-------|
| `j2ee`   | `j2ee`         | Favourite category DOGS |
| `ACID`   | `ACID`         | Favourite category CATS |

Passwords are stored as **bcrypt hashes** in the `signon` table after running the seed command.

## Seeding rules

- Command: **`jpetstore-seed`** (or `python -m jpetstore.scripts.seed`).
- Allowed when `APP_ENV` is **`development`** or **`test`** only — **refuses** when `APP_ENV=production`.
- Target **development** database via `DATABASE_URL` → database **`jpetstore`**, user **`jpetstore_app`**.
- For automated MySQL tests, use **`jpetstore_test`** via `TEST_DATABASE_URL`.
- Seeder is **idempotent**; repeated runs do not duplicate catalog or account rows.

## MySQL connection (local)

Set host and port to match your MySQL 8 instance (confirm with `Test-NetConnection`):

```
mysql+pymysql://jpetstore_app:<password>@127.0.0.1:3306/jpetstore?charset=utf8mb4
```

Integration tests:

```
mysql+pymysql://jpetstore_app:<password>@127.0.0.1:3306/jpetstore_test?charset=utf8mb4
```

Database creation: `scripts/mysql-local-setup.sql`.
