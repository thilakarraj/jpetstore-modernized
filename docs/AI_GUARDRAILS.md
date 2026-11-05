# AI Guardrails — JPetStore Python Modernization

Rules for human and AI contributors. Violations block merge until corrected.

---

## 1. Scope guardrails

| Rule | Enforcement |
|------|-------------|
| G-01 | Do not add business capabilities not listed in `FUNCTIONAL_REQUIREMENTS.md` |
| G-02 | Do not add Kafka, Kubernetes, Redis, Elasticsearch, or separate message brokers |
| G-03 | Do not modify `jpetstore-6/` Java sources |
| G-04 | Maximum deployable units: Gateway + Catalog + Account + Order + MySQL (Compose) |
| G-05 | Do not merge microservices into a single FastAPI app without ADR and human approval |

---

## 2. Security guardrails

| Rule | Detail |
|------|--------|
| S-01 | Passwords: bcrypt only; never log or return password fields |
| S-02 | JWT: HS256 with `JWT_SECRET` from env; minimum 32 bytes entropy in production docs |
| S-03 | `/internal/*` routes bind `0.0.0.0` but Compose network must not publish internal ports to host |
| S-04 | Gateway is sole public port (8080); MySQL not exposed in production profile (dev may map 3306) |
| S-05 | Credit card values: store only as required for parity; log with mask `****9999` or omit |
| S-06 | SQL: SQLAlchemy parameterized queries only; no f-string SQL |
| S-07 | AI-generated crypto/auth code requires **human security review** before merge |
| S-08 | Dependencies: pin versions in `pyproject.toml`; run `pip audit` or equivalent in CI when available |

**Security review checklist (human):**

- [ ] Auth bypass paths on Order/Account protected routes  
- [ ] IDOR on `GET /orders/{id}` and cart ids  
- [ ] Internal endpoints unreachable from Gateway routes  
- [ ] Secrets not in git history  

---

## 3. Data and transaction guardrails

| Rule | Detail |
|------|--------|
| D-01 | Order placement: exactly one DB transaction for sequence + inventory + orders + orderstatus + lineitem |
| D-02 | Do not split inventory decrement to Catalog Service |
| D-03 | Idempotency-Key: unique constraint `(username, key)`; replay must not decrement inventory twice |
| D-04 | Cross-schema data: use HTTP between services, not MySQL cross-database joins |
| D-05 | Seed data must derive from legacy `jpetstore-hsqldb-dataload.sql` (MySQL-adapted) |

---

## 4. API guardrails

| Rule | Detail |
|------|--------|
| A-01 | Public paths must match `API_SPECIFICATION.md` prefixes |
| A-02 | Error messages for FR-mandated text must match exactly (case/punctuation) |
| A-03 | Breaking API changes require version bump `v2` and ADR |
| A-04 | OpenAPI is generated from FastAPI; diff against spec in review |

---

## 5. AI code generation guardrails

| Rule | Detail |
|------|--------|
| AI-01 | **Repository-grounded:** every behavioral claim must reference legacy file or FR/TR ID |
| AI-02 | **No invented requirements** — if missing, add to `ANALYSIS_GAPS.md` and stop |
| AI-03 | **Minimal diff:** one service slice per generation session |
| AI-04 | **No placeholder** `TODO` in production paths for FR-covered behavior |
| AI-05 | **Imports at top of file** (project rule) |
| AI-06 | **Exhaustive handling** for enums/unions in Python where applicable |
| AI-07 | Do not disable tests, hooks, or type checks to pass CI |
| AI-08 | Copy-paste from unknown Stack Overflow snippets for security code — forbidden; use stdlib/`passlib`/documented patterns only |

---

## 6. Human approval matrix

| Action | Approver |
|--------|----------|
| Merge to main | Human reviewer |
| Parity deviation | Product/architect + ADR |
| New env var / secret name | Human |
| AI-only PR without tests | **Reject** |
| AI-only PR touching auth/order tx | Human security + logic review |

---

## 7. Automated validation gates (must pass)

1. `ruff check .`  
2. `mypy services/` (or project equivalent)  
3. `pytest services/<name>/tests` for changed service  
4. `pytest tests/e2e` before release tag  
5. Manual or scripted check: `curl /health/ready` all green after Compose up  

AI agents must run gates 1–3 locally after edits.

---

## 8. AI-generated code acceptance criteria

Code is **accepted** when all hold:

1. **Traceability:** PR lists FR/ADR IDs.  
2. **Tests:** New logic has pytest coverage; order path includes rollback test.  
3. **Spec sync:** `API_SPECIFICATION.md` updated if routes changed.  
4. **Observability:** Uses `jpetstore_common` JSON logger; includes `request_id`.  
5. **Failure modes:** HTTP status codes match spec; no bare `500` without log context.  
6. **Parity/improvement labeled** in PR template.  
7. **No guardrail violations** from §1–5.

**Reject** if: silent behavior change, new table without TARGET doc update, or missing idempotency on order POST.

---

## 9. Logging prohibitions

Never log: `password`, `Authorization` header, full JWT, full `credit_card`, `JWT_SECRET`.

Allowed: `username`, `order_id`, `item_id`, masked card last four if needed for support.

---

## 10. Escalation

When legacy behavior is ambiguous (`ANALYSIS_GAPS.md`):

1. Stop implementation.  
2. Propose verification test against Java app or document `[A]`.  
3. Human decides; record in ADR if decision is durable.

---

## 11. PR template (recommended)

```markdown
## FR / ADR
- FR-x.y, ADR-00z

## Parity or improvement
- [ ] Parity  [ ] Improvement (explain)

## Guardrails checked
- [ ] G-01–G-05  [ ] S-01–S-08  [ ] D-01–D-05

## Tests
- `pytest ...`

## Human review required
- [ ] Auth/order  [ ] Security  [ ] None
```
