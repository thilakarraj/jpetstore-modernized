# JPetStore — Security Remediation Plan

Maps **JPET-SEC-*** findings to remediation for the **Python** application (FastAPI, MySQL, Docker Compose). Legacy Java remains unchanged.

**Phasing:** P0 = before any public demo; P1 = before production-like deployment; P2 = hardening.

---

## Phase 0 — Governance (immediate)

| Action | Owner | Deliverable |
|--------|-------|-------------|
| Review and sign `SECURITY_ASSESSMENT.md` | Architect / Security | Approved finding list |
| Sign accepted risks in `SECURITY_RISK_REGISTER.md` | Product | Written acceptance |
| Enforce `AI_GUARDRAILS.md` on generated code | Engineering | PR checklist |

---

## Phase 1 — P0 controls (implementation start)

| Finding | Remediation | Service | Changes legacy behavior? |
|---------|-------------|---------|---------------------------|
| JPET-SEC-001 | Bcrypt hashes in `signon`; verify via passlib/bcrypt | Account | **Yes** (improvement) |
| JPET-SEC-002 | Reject `PUT /account/me` without valid JWT; no anonymous profile writes | Account + Gateway | **Yes** |
| JPET-SEC-003 | Ignore client-supplied username; use JWT `sub` as sole identity key | Account | **Yes** |
| JPET-SEC-004 | JSON API: no cookie session; require `Authorization` + optional CSRF N/A; for future HTML BFF use SameSite + CSRF token | Gateway | **Yes** (transport) |
| JPET-SEC-007 | Pydantic max lengths; HTML-escape all UI output; API returns plain text fields | All + UI | **Yes** for XSS surface |
| JPET-SEC-011 | Store card fields only if parity required; mask in responses/logs; never log full PAN | Order | **Partial** — storage parity, display masked optional |
| JPET-SEC-015 | `GET /orders/{id}`: `order.userid == JWT sub` | Order | **No** (matches Java) |
| JPET-SEC-016 | SQLAlchemy `text()` only with bound params; ban string SQL concat | All | **No** |
| JPET-SEC-021 | Single transaction in `place_order()` | Order | **No** |
| JPET-SEC-023 | Require `Idempotency-Key` on `POST /orders` | Order | **Yes** (improvement) |

**Exit criteria:** SEC-T-001 through SEC-T-004, SEC-T-007, SEC-T-015, SEC-T-021, SEC-T-023 pass in CI.

---

## Phase 2 — P1 controls (pre-release)

| Finding | Remediation | Service | Changes legacy behavior? |
|---------|-------------|---------|---------------------------|
| JPET-SEC-005 | POST/DELETE for cart mutations only | Order | **Yes** (HTTP method) |
| JPET-SEC-008 | Serve banner as URL reference or sanitize HTML subset | Account/Catalog | **Possible** |
| JPET-SEC-009 | Return description as text; client renders safe subset | Catalog | **Possible** |
| JPET-SEC-018 | Validate password length, match on register; optional complexity | Account | **Yes** |
| JPET-SEC-017 | Pydantic models with `model_config extra=forbid` | All | **Yes** |
| JPET-SEC-019 | Document parity; optional `STRICT_INVENTORY=true` env | Order | **Optional improvement** |
| JPET-SEC-022 | `SELECT … FOR UPDATE` on sequence row | Order | **Yes** (improvement) |
| JPET-SEC-024 | Gateway middleware: e.g. 10 req/min/login IP, 60 req/min/search | Gateway | **Yes** |
| JPET-SEC-025 | `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy-Report-Only` → enforce | Gateway | **Yes** |
| JPET-SEC-026 | CORS allowlist env `CORS_ORIGINS` | Gateway | **New** |
| JPET-SEC-030 | JSON logs; events: `login_success`, `login_failure`, `order_created` | All | **Yes** |
| JPET-SEC-032 | CI: `pip-audit`, Bandit, Semgrep, Trivy, Gitleaks | CI | **No** |

**Exit criteria:** Full `SECURITY_TEST_CASES.md` P0+P1 green; ZAP baseline scan no High alerts on auth/order flows.

---

## Phase 3 — P2 / operational

| Finding | Remediation | Changes legacy behavior? |
|---------|-------------|---------------------------|
| JPET-SEC-012 | No default credentials in UI/docs for non-dev | N/A |
| JPET-SEC-014 | Secure cookie N/A for JWT; if refresh cookies added, set HttpOnly/Secure/SameSite | **New** |
| JPET-SEC-029 | MySQL not on public interface; strong root password; app users least privilege per schema | **New** |
| JPET-SEC-031 | Document backup/restore for MySQL volume | Ops |
| JPET-SEC-006 | Sign-off = discard token client-side | **Yes** |

---

## Remediation ↔ Python requirements matrix

| Requirement | Phase | Verification |
|-------------|-------|--------------|
| JWT auth + validation | 1 | SEC-T-036 suite |
| Bcrypt passwords | 1 | SEC-T-001 |
| Centralized authz | 1 | SEC-T-002, SEC-T-003, SEC-T-015 |
| SQLAlchemy parameterized | 1 | Bandit + SEC-T-016 |
| Input validation | 1–2 | SEC-T-017, SEC-T-018 |
| Rate limiting | 2 | SEC-T-024 |
| Secret management | 1 | Gitleaks + env review |
| Payment minimization | 1–2 | SEC-T-011 |
| Transaction + idempotency | 1 | SEC-T-021, SEC-T-023 |
| Security headers + CORS | 2 | SEC-T-025, SEC-T-026 |
| Dependency + container scan | 2 | SEC-T-032, SEC-T-033 |
| Logging redaction | 2 | SEC-T-030 |

---

## Implementation order (security-driven)

1. Account: hashing + JWT issue + auth middleware patterns  
2. Gateway: JWT verify + headers + rate limit skeleton  
3. Order: authz on orders + transactional place_order + idempotency  
4. Catalog: read-only public + internal network  
5. CI security gates  
6. ZAP baseline (manual or CI optional)  

---

## Do not implement without approval

- Admin/RBAC roles (**JPET-SEC-034**)  
- New payment processor integration  
- Removing card columns from DB (breaks parity unless risk accepted)
