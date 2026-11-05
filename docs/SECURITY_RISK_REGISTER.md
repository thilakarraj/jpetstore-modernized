# JPetStore — Security Risk Register

Tracks **accepted risks** for the Python modernization and **residual legacy risks**. Review quarterly or when scope changes.

**Risk scoring:** Likelihood (L: 1–5) × Impact (I: 1–5) = Score  
**Treatment:** Mitigate | Accept | Transfer | Avoid  

---

## 1. Active accepted risks (Python target)

| Risk ID | Description | L | I | Score | Treatment | Owner | Review date | Rationale |
|---------|-------------|---|---|-------|-----------|-------|-------------|-----------|
| R-001 | Demo payment data stored in MySQL (`credit_card` column) | 2 | 4 | 8 | Accept | Product | 2026-12-01 | Parity with JPetStore demo; not real PCI scope; masked in logs (SEC-D-13) |
| R-002 | Negative inventory allowed at order submit | 3 | 3 | 9 | Accept | Product | 2026-12-01 | Behavioral parity (JPET-SEC-019); optional `STRICT_INVENTORY` later |
| R-003 | HS256 symmetric JWT secret | 2 | 4 | 8 | Accept | Engineering | 2026-12-01 | Assessment simplicity; rotate secret; plan RS256 for prod |
| R-004 | Sync HTTP coupling Order→Catalog/Account | 3 | 3 | 9 | Accept | Architect | 2026-12-01 | No Kafka per constraint; failure → degraded add-to-cart |
| R-005 | Duplicate products in multi-word search | 2 | 1 | 2 | Accept | Product | 2026-12-01 | Legacy parity (TR-6.5) |
| R-006 | No server-side refresh token / revoke | 3 | 3 | 9 | Accept | Product | 2026-12-01 | Short TTL mitigates; logout client-side |
| R-007 | Internal service trust of `X-User-Id` header | 2 | 5 | 10 | Mitigate | Engineering | 2026-12-01 | Mitigate via Docker network isolation + no public internal ports |
| R-008 | Shared MySQL host, separate schemas | 2 | 4 | 8 | Accept | Architect | 2026-12-01 | Assessment deadline; not full DB-per-service isolation |
| R-009 | Seed credentials `j2ee`/`j2ee` in dev | 4 | 2 | 8 | Mitigate | Engineering | 2026-12-01 | Document; disable in prod-like env |
| R-010 | orderstatus.linenum = order_id quirk | 1 | 1 | 1 | Accept | Engineering | 2026-12-01 | Data model parity |

---

## 2. Legacy risks (Java JPetStore 6 — reference only)

Not accepted for Python; listed for traceability.

| Risk ID | Finding | Severity | Python action |
|---------|---------|----------|---------------|
| L-001 | JPET-SEC-001 Plaintext passwords | Critical | Mitigated SEC-D-02 |
| L-002 | JPET-SEC-002 Unauthenticated account edit | Critical | Mitigated SEC-D-04 |
| L-003 | JPET-SEC-003 Account IDOR | High | Mitigated SEC-D-04 |
| L-004 | JPET-SEC-004 CSRF order confirm | High | Mitigated SEC-D-09 |
| L-005 | JPET-SEC-007 Stored XSS | High | Mitigated SEC-D-08 |
| L-006 | JPET-SEC-011 Card data at rest | High | Partial accept R-001 |

---

## 3. Risks under mitigation (in progress)

| Risk ID | Description | Target mitigation | Status |
|---------|-------------|-------------------|--------|
| M-001 | Dependency CVEs in Python stack | pip-audit + pinned deps | Open until CI live |
| M-002 | Container image vulnerabilities | Trivy gate | Open until images built |
| M-003 | Brute-force login | SEC-D-11 rate limit | Open until Gateway done |
| M-004 | Double order submit | SEC-T-023 idempotency | Open until Order service done |

---

## 4. Rejected / avoided risks

| Risk | Decision |
|------|----------|
| Admin RBAC without approval | Avoid (SEC-D-20) |
| Public `/internal/*` routes | Avoid |
| Kafka for auth events | Avoid (scope) |
| Storing JWT in localStorage (if SPA) | Document; prefer memory or httpOnly if cookies added later |

---

## 5. Risk review triggers

- New external exposure of MySQL or internal APIs  
- Change from HS256 to no auth on Order routes  
- Real payment integration requested  
- Penetration test findings  

---

## 6. Sign-off

| Stakeholder | Accepted risks (IDs) | Date |
|-------------|---------------------|------|
| Product | R-001, R-002, R-005, R-010 | |
| Engineering | R-003, R-004, R-007, R-008, R-009 | |
| Security | All with mitigations M-* tracked | |

*Incomplete sign-off blocks production deployment; assessment/dev may proceed with R-001–R-010 documented.*

---

## 7. Mapping to remediation phases

| Phase | Closes |
|-------|--------|
| P0 | L-001–L-005, M-004 |
| P1 | M-001–M-003 |
| P2 | Operational items SEC-T-031 |
