# JPetStore Python — Security Decisions

Normative security requirements for the new application. Legacy behavior cited where parity applies.

---

## 1. Decision summary

| ID | Topic | Decision |
|----|-------|----------|
| SEC-D-01 | Authentication model | JWT access tokens (HS256); no server-side session for API |
| SEC-D-02 | Password storage | Bcrypt, cost factor 12 (tune in prod) |
| SEC-D-03 | Authorization | Gateway validates JWT; services trust `X-User-Id` from Gateway on private network only |
| SEC-D-04 | Account updates | Identity from JWT `sub` only; forbid username in request body |
| SEC-D-05 | Registration | 201 without token (FR-3.6 parity) |
| SEC-D-06 | SQL | SQLAlchemy 2 Core/ORM; no dynamic SQL string building from user input |
| SEC-D-07 | Input | Pydantic v2 models; `extra=forbid` on write DTOs |
| SEC-D-08 | Output | JSON API default; HTML clients must escape |
| SEC-D-09 | CSRF | Bearer JWT in header → CSRF risk reduced; if cookie auth added later, require CSRF tokens |
| SEC-D-10 | CORS | Explicit allowlist; no `*` with credentials |
| SEC-D-11 | Rate limit | Gateway: login 10/min/IP; global 300/min/IP baseline |
| SEC-D-12 | Secrets | Env vars; `.env` gitignored; Gitleaks in CI |
| SEC-D-13 | Payment data | Store columns for parity; log mask; document PCI out-of-scope |
| SEC-D-14 | Orders | Single DB transaction; `Idempotency-Key` required |
| SEC-D-15 | Inventory | Parity: allow negative qty unless `STRICT_INVENTORY=1` |
| SEC-D-16 | Internal APIs | Not routed via Gateway; Docker network only |
| SEC-D-17 | Headers | Gateway adds HSTS (TLS), nosniff, frame deny, CSP |
| SEC-D-18 | Logging | JSON structured; redact password, Authorization, credit_card |
| SEC-D-19 | Supply chain | pip-audit, Bandit, Semgrep, Trivy in CI |
| SEC-D-20 | RBAC/Admin | Not implemented without explicit approval |

---

## 2. JWT authentication and validation

### 2.1 Token format

- **Type:** JWT access token  
- **Algorithm:** HS256 (shared secret) for assessment; document migration path to RS256 for multi-node  
- **Claims:** `sub` (username), `iat`, `exp`, optional `jti`  
- **TTL:** 60 minutes default (`JWT_EXPIRE_MINUTES`)

### 2.2 Issuance

- Only **Account Service** `POST /auth/login` after bcrypt verify  
- Never issue token on register (SEC-D-05)

### 2.3 Validation (Gateway)

1. Parse `Authorization: Bearer …`  
2. Verify signature with `JWT_SECRET`  
3. Reject `alg` not in allowlist (`HS256` only)  
4. Reject expired / missing `sub`  
5. Forward `X-User-Id: {sub}` to Order/Account protected routes  

### 2.4 Validation (services)

- Order/Account **must not** parse JWT directly in baseline; rely on Gateway + network isolation  
- If service exposed beyond Gateway, duplicate JWT validation (future ADR)

### 2.5 Logout

- Client deletes token; optional future denylist out of scope  

### 2.6 Python requirements checklist

- [ ] Constant-time comparison not needed for JWT verify (library handles)  
- [ ] Secret length ≥ 32 bytes  
- [ ] Unit tests: SEC-T-036  

---

## 3. Bcrypt / Argon2 password hashing

- **Primary:** bcrypt via passlib or `bcrypt` library  
- **Argon2:** Acceptable alternative if team standard; document in ADR if switched  
- **Migration:** Seed script hashes `j2ee`/`ACID` passwords for dev  
- **Never:** Log plaintext password or hash in application logs  

---

## 4. Centralized authorization and ownership

| Resource | Rule |
|----------|------|
| `GET/PUT /account/me` | JWT required; `sub` is row key |
| `GET /orders` | JWT; filter `userid = sub` |
| `GET /orders/{id}` | JWT; `order.userid == sub` else 403 |
| `POST /orders` | JWT; order `userid` from `sub`, not body |
| Cart | Guest: `X-Cart-Id`; authenticated: bind cart to `sub` |
| Catalog reads | Public |

Implement shared dependency `require_user()` in `jpetstore_common` for services behind Gateway.

---

## 5. SQLAlchemy parameterized queries

- Use `session.execute(select(...).where(...))` with bound parameters  
- Prohibit: f-strings, `%` formatting, concatenation for SQL  
- Migrations via Alembic; no raw DDL from user input  

---

## 6. Input validation and output safety

- Max lengths aligned with MySQL schema (`varchar` sizes in `DATA_MODEL.md`)  
- Email/phone format validation minimal (parity with Java — no strict regex in legacy)  
- Enum fields: `language_preference`, `favourite_category_id` allowlist  
- HTML in catalog descriptions returned as strings; not interpreted by API  

---

## 7. Rate limiting

- Implement at Gateway (middleware or reverse proxy)  
- Endpoints: `/auth/login`, `/auth/register`, `/catalog/products/search`, `/orders`  
- Response: `429` with `Retry-After`  

---

## 8. Secure configuration and secret management

| Secret | Storage |
|--------|---------|
| `JWT_SECRET` | Env |
| MySQL passwords | Env per service schema user |
| No secrets in git | Gitleaks enforced |

Compose: use `env_file: .env` local only; document `.env.example` placeholders.

---

## 9. Payment data minimization

- **Parity:** Persist `credit_card`, `expiry_date`, `card_type` on order row (demo)  
- **Improvement:** Mask PAN in GET responses (`****9999`) — document as UX change  
- **Logs:** Never log full PAN  
- **Scope:** Not PCI compliant; disclaimer in README  

---

## 10. Transaction atomicity and idempotency

Match `OrderService.insertOrder` ordering with improvements:

1. Begin transaction  
2. Idempotency check  
3. Lock sequence row  
4. Decrement inventory per line  
5. Insert order, orderstatus, lineitems  
6. Update sequence  
7. Clear cart  
8. Commit  

`Idempotency-Key` stored with unique `(username, key)`.

---

## 11. Security headers and CORS

**Gateway response headers (baseline):**

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; frame-ancestors 'none'
Strict-Transport-Security: max-age=31536000 (HTTPS deployments only)
```

**CORS:**

```
Access-Control-Allow-Origin: <from CORS_ORIGINS env>
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type, Idempotency-Key, X-Cart-Id
```

No credentials mode with wildcard origin.

---

## 12. Dependency scanning and container security

| Tool | When |
|------|------|
| pip-audit | Every PR |
| Bandit | Every PR |
| Semgrep (OWASP rules) | Every PR |
| Trivy | On Docker build |
| Gitleaks | Every PR |

Base images: pin `python:3.12-slim` and `mysql:8` digests in Compose for reproducibility.

---

## 13. Structured logging with redaction

- Format: JSON lines to stdout  
- Fields: `timestamp`, `level`, `service`, `request_id`, `path`, `status`, `duration_ms`  
- Redaction filter on keys: `password`, `authorization`, `credit_card`, `jwt`, `token`  
- Security events at INFO: `auth.login.failure`, `auth.login.success`, `order.placed`, `authz.denied`  

---

## 14. Parity vs improvement quick reference

| Legacy issue | Python stance |
|--------------|---------------|
| Plaintext passwords | **Fix** (SEC-D-02) |
| Unauthenticated edit | **Fix** (SEC-D-04) |
| CSRF on forms | **Fix** via JWT API |
| Stored XSS in JSP | **Fix** via encoding |
| Negative inventory | **Parity** default (SEC-D-15) |
| Store credit card | **Parity** with log mask (SEC-D-13) |
| No rate limit | **Fix** (SEC-D-11) |

---

## 15. Approval record

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Architect | | | |
| Security | | | |
| Product | | | |

*Complete before backend implementation.*
