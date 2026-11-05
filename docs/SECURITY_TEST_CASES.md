# JPetStore — Security Test Cases

Automated tests use **pytest** unless noted. IDs map to `SECURITY_ASSESSMENT.md`.

**Conventions:**

- `BASE` = Gateway URL (e.g. `http://localhost:8080/api/v1`)  
- Tests against Python unless labeled `[LEGACY]`  
- P0 = release blocker; P1 = pre-production; P2 = recommended  

---

## SEC-T-001 — Password hashing (P0)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-001 |
| **Objective** | Passwords never stored or compared in plaintext |
| **Steps** | 1. Register user via API. 2. Query DB `signon` row. 3. Login with correct password. 4. Login with wrong password fails. |
| **Expected** | Hash starts with `$2b$` (bcrypt); no plaintext; 401 on bad password |
| **Automation** | `tests/security/test_password_hashing.py` |

---

## SEC-T-002 — Unauthenticated account update blocked (P0)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-002 |
| **Objective** | Anonymous client cannot update any account |
| **Steps** | `PUT /account/me` without `Authorization` |
| **Expected** | `401 Unauthorized`; DB unchanged |
| **Automation** | `tests/security/test_account_authz.py` |

---

## SEC-T-003 — Account update IDOR blocked (P0)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-003 |
| **Objective** | User A cannot modify user B profile |
| **Steps** | Login as A; send body with `username: B` or path tampering |
| **Expected** | Only A’s row updated; B unchanged |
| **Automation** | `tests/security/test_account_authz.py` |

---

## SEC-T-004 — Order confirm requires authenticated caller (P0)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-004 (Python mitigates via JWT, not CSRF token) |
| **Objective** | Unauthenticated `POST /orders` rejected |
| **Steps** | POST without JWT |
| **Expected** | `401` |
| **Automation** | `tests/security/test_order_authz.py` |

---

## SEC-T-005 — Cart mutations require appropriate auth (P1)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-005 |
| **Objective** | Cart endpoints use POST/DELETE; guest cart isolated |
| **Steps** | User B cannot modify user A cart (different JWT / cart id) |
| **Expected** | `403` or empty cart isolation |
| **Automation** | `tests/security/test_cart_isolation.py` |

---

## SEC-T-006 — Sign-off (P2)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-006 |
| **Objective** | After client discards token, protected routes fail |
| **Steps** | Login; discard token; call `/account/me` |
| **Expected** | `401` |

---

## SEC-T-007 — Stored XSS prevented in profile fields (P0)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-007 |
| **Objective** | HTML in `first_name` not executable in API JSON consumers |
| **Steps** | Register with `first_name=<script>alert(1)</script>`; GET profile |
| **Expected** | Literal string in JSON; UI tests escape if HTML client exists |
| **Automation** | pytest + optional Playwright assert no alert |

---

## SEC-T-008 — Banner HTML (P1)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-008 |
| **Objective** | Banner content policy documented; no arbitrary script in API |
| **Steps** | Profile with banner; inspect response |
| **Expected** | Sanitized or URL-only banner |

---

## SEC-T-009 — Product description encoding (P1)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-009 |
| **Objective** | Catalog API returns text; no automatic HTML execution |
| **Steps** | GET product with HTML in description |
| **Expected** | JSON string; client responsible for rendering |

---

## SEC-T-010 — Error message reflection (P2)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-010 |
| **Objective** | Error messages do not reflect unescaped user input |
| **Steps** | Search with keyword containing `<>` |
| **Expected** | Encoded in JSON |

---

## SEC-T-011 — Payment data in logs and responses (P0)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-011 |
| **Objective** | Logs do not contain full credit card; API masks if configured |
| **Steps** | Place order; capture logs; GET order |
| **Expected** | No full PAN in logs; response per parity decision |

---

## SEC-T-012 — Default credentials (P2)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-012 |
| **Objective** | Dev seed documented; production docs warn to rotate |
| **Manual** | Review UI templates |

---

## SEC-T-013 — Session fixation (P2, legacy)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-013 |
| **[LEGACY]** | Optional manual test on Java Tomcat |

---

## SEC-T-014 — Cookie flags (P2, legacy)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-014 |
| **[LEGACY]** | Inspect `Set-Cookie` for `JSESSIONID` in browser devtools |

---

## SEC-T-015 — Order view IDOR (P0)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-015 |
| **Objective** | User A cannot GET user B order |
| **Steps** | Create order as B; GET as A |
| **Expected** | `403` + message parity optional |
| **Automation** | `tests/security/test_order_authz.py` |

---

## SEC-T-016 — SQL injection regression (P0)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-016 |
| **Objective** | Malicious search keyword does not alter SQL |
| **Steps** | `keyword=' OR '1'='1` |
| **Expected** | Empty or literal match; no error leak; Bandit clean |
| **Automation** | pytest + Bandit |

---

## SEC-T-017 — Mass assignment (P1)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-017 |
| **Objective** | Extra JSON fields rejected |
| **Steps** | POST register with `"status": "ADMIN"` |
| **Expected** | `422` or field ignored with default only |

---

## SEC-T-018 — Password policy (P1)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-018 |
| **Objective** | Mismatched passwords rejected on register |
| **Steps** | Register with password ≠ repeated (if exposed) or API validation |
| **Expected** | `422` |

---

## SEC-T-019 — Negative inventory parity (P1)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-019 |
| **Objective** | Document behavior: order exceeding stock succeeds with negative qty |
| **Steps** | Set inventory 1; order qty 5 |
| **Expected** | Order created; qty negative if parity mode |

---

## SEC-T-020 — Order total integrity (P1)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-020 |
| **Objective** | Server computes total from cart lines at submit |
| **Steps** | Attempt API body with tampered `total_price` |
| **Expected** | Server ignores client total; uses cart |

---

## SEC-T-021 — Order transaction rollback (P0)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-021 |
| **Objective** | Failed insert rolls back inventory |
| **Steps** | Inject failure after decrement (test hook) |
| **Expected** | Inventory unchanged |

---

## SEC-T-022 — Sequence concurrency (P2)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-022 |
| **Objective** | Parallel orders get unique IDs |
| **Steps** | Concurrent `POST /orders` with distinct keys |
| **Expected** | Unique `order_id` |

---

## SEC-T-023 — Idempotency (P0)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-023 |
| **Objective** | Same `Idempotency-Key` does not double-charge inventory |
| **Steps** | POST twice same key |
| **Expected** | One order; second `201` same body or `409` per spec |

---

## SEC-T-024 — Rate limiting (P1)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-024 |
| **Objective** | Login endpoint throttled |
| **Steps** | >N failed logins from one IP |
| **Expected** | `429 Too Many Requests` |

---

## SEC-T-025 — Security headers (P1)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-025 |
| **Objective** | Gateway sets required headers |
| **Steps** | GET any route; inspect headers |
| **Expected** | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` (or SAMEORIGIN), CSP present |

---

## SEC-T-026 — CORS (P1)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-026 |
| **Objective** | Untrusted origin blocked |
| **Steps** | Preflight from `https://evil.example` |
| **Expected** | No `Access-Control-Allow-Origin: *` with credentials |

---

## SEC-T-027 — SSRF (P2)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-027 |
| **Objective** | No user-controlled outbound URLs |
| **N/A** unless feature added |

---

## SEC-T-028 — Open redirect (P2)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-028 |
| **Objective** | No redirect param to external URL |
| **Steps** | Fuzz redirect query params if any |

---

## SEC-T-029 — MySQL network exposure (P1)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-029 |
| **Objective** | Port 3306 not on host in prod compose profile |
| **Steps** | `docker compose config` review |

---

## SEC-T-030 — Log redaction (P1)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-030 |
| **Objective** | Logs omit password/JWT/PAN |
| **Steps** | Login + order; grep logs |
| **Expected** | Redacted |

---

## SEC-T-031 — Backup (P2)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-031 |
| **Manual** | Runbook exists |

---

## SEC-T-032 — Dependency scan (P1)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-032 |
| **CI** | `pip-audit`, Bandit, Semgrep fail on High |

---

## SEC-T-033 — Container scan (P1)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-033 |
| **CI** | Trivy scan images; no Critical unfixed |

---

## SEC-T-034 — No admin RBAC (P0 process)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-034 |
| **Objective** | No admin routes without approval |
| **Review** | Grep `/admin` routes |

---

## SEC-T-035 — Edit profile requires auth (P1)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-035 |
| **Objective** | `GET /account/me` requires JWT |
| **Expected** | `401` without token |

---

## SEC-T-036 — JWT security (P0)

| Field | Value |
|-------|--------|
| **Finding** | JPET-SEC-036 |
| **Tests** | |
| | Expired token → `401` |
| | Tampered signature → `401` |
| | `alg: none` rejected |
| | Wrong `sub` cannot access orders |
| **Automation** | `tests/security/test_jwt.py` |

---

## Legacy regression pack `[LEGACY]` (optional)

| ID | Description |
|----|-------------|
| SEC-L-001 | Manual confirm JPET-SEC-002 on Java Tomcat POST `/account/edit` without cookie |
| SEC-L-002 | Verify OrderControllerTest IDOR test remains passing in Java |

---

## Release gate checklist

- [ ] All P0 pytest green  
- [ ] Bandit + pip-audit + Semgrep CI green  
- [ ] Trivy no Critical on service images  
- [ ] Gitleaks clean  
- [ ] OWASP ZAP baseline: no High on auth/order flows  
- [ ] `SECURITY_RISK_REGISTER.md` signed for accepted parity risks  
