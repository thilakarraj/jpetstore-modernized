# JPetStore 6 — Security Assessment

**Assessment date:** 2026-11-04  
**Scope:** `jpetstore-6/` source (Java, JSP, MyBatis, Spring XML, `pom.xml`, `web.xml`) — **read-only review, no code changes**  
**Target context:** Python modernization per `docs/TARGET_ARCHITECTURE.md` (Gateway + services; security controls in §6–§8 below)

---

## 1. Methodology

Static review of controllers, services, mapper XML, JSP output encoding, session usage, transaction boundaries, seed data, and deployment descriptors. No dynamic penetration test was executed in this pass. Findings marked **Requires Runtime Validation** need confirmation in a running Tomcat deployment.

**Severity scale:** Critical / High / Medium / Low  
**Status:** Confirmed | Potential | Requires Runtime Validation

---

## 2. Finding register (summary table)

| Finding ID | Category | Evidence | Severity | Exploitation Scenario | Remediation | Test Case | Status |
|------------|----------|----------|----------|----------------------|-------------|-----------|--------|
| JPET-SEC-001 | Authentication / passwords | `signon.password` plaintext; `AccountMapper.xml` L73, L123–129; `jpetstore-hsqldb-dataload.sql` L19–20 | Critical | DB or backup leak exposes all user passwords; offline cracking | Bcrypt/Argon2 in Python; never store reversible passwords | SEC-T-001 | Confirmed |
| JPET-SEC-002 | Authorization | `AccountController.editAccount` L177–183 — no auth check before `updateAccount` | Critical | Anonymous attacker POSTs crafted form to `/account/edit` with `username=victim` and changes victim email/password/profile | Require JWT; bind updates to `sub`; reject unauthenticated writes | SEC-T-002 | Confirmed |
| JPET-SEC-003 | Authorization / IDOR | `EditAccountForm.jsp` L22 hidden `username`; `editAccount` uses `@ModelAttribute` username in `AccountMapper` WHERE | High | Logged-in user tampering hidden field updates another user’s account | Ignore client username; use token `sub` only | SEC-T-003 | Confirmed |
| JPET-SEC-004 | CSRF | `ConfirmOrder.jsp` POST `/order/new`; `OrderController.newOrder` L146–148 confirms on `confirmed=true` | High | Victim logged in visits malicious page that auto-POSTs order confirm; order placed and cart cleared | CSRF token or SameSite cookies + POST-only mutations in Python | SEC-T-004 | Confirmed |
| JPET-SEC-005 | CSRF | `CartController` GET `/cart/addItem`, `/cart/removeItem`; JSP links `Product.jsp` L40 | Medium | Third-party site triggers victim browser to add/remove cart items | POST + CSRF token for cart mutations | SEC-T-005 | Confirmed |
| JPET-SEC-006 | CSRF | `AccountController.signoff` GET `/account/signoff` | Low | CSRF forces logout | POST sign-off optional in Python | SEC-T-006 | Confirmed |
| JPET-SEC-007 | XSS (stored) | `Main.jsp` L24 `Welcome ${sessionScope.accountBean.account.firstName}!` unescaped | High | Register user with `firstName=<script>…</script>`; script runs for all viewers of welcome | Context-aware encoding (HTML); Pydantic + template autoescape | SEC-T-007 | Confirmed |
| JPET-SEC-008 | XSS (stored) | `IncludeBottom.jsp` L28 `${account.bannerName}` unescaped HTML from DB | Medium | If `bannerdata` or profile path injects HTML/JS, executes in browser (seed uses `<image …>`) | Sanitize or encode; CSP; treat banner as trusted static content only | SEC-T-008 | Confirmed |
| JPET-SEC-009 | XSS (stored) | `SearchProducts.jsp` L32–34, `Item.jsp` L26, `Category.jsp` L24 — `${product.description}` etc. | Medium | Catalog HTML in DB rendered raw (seed includes `<image src=…>`); poisoned DB → XSS | Encode on output or strict HTML sanitizer; Python API returns structured fields | SEC-T-009 | Confirmed |
| JPET-SEC-010 | XSS (reflected) | `IncludeTop.jsp` L89–90 `${message}` without `<c:out>` | Low | If future code adds user input to `message`, reflected XSS (today mostly static strings) | Always encode `message` | SEC-T-010 | Potential |
| JPET-SEC-011 | Payment data | `OrderMapper.xml` insert stores `CREDITCARD`, `EXPRDATE`; `ViewOrder.jsp` displays card | High | DB breach exposes PAN-like demo data; violates PCI if treated as real | Minimize storage; tokenize; mask in UI/logs (Python ADR-014 parity decision) | SEC-T-011 | Confirmed |
| JPET-SEC-012 | Sensitive exposure | `SignonForm.jsp` L24–25 default `value="j2ee"` username/password | Low | Encourages shared demo credentials; shoulder surfing | Remove defaults in any production-like env | SEC-T-012 | Confirmed |
| JPET-SEC-013 | Session management | `AccountController.signon` L98 — no `session.invalidate()` before login | Medium | Session fixation if attacker sets victim session id pre-login | Regenerate session ID on login in Python (JWT avoids server session) | SEC-T-013 | Potential |
| JPET-SEC-014 | Session management | `web.xml` — no `<cookie-config>` / `<session-config>` | Medium | `JSESSIONID` flags (HttpOnly, Secure, SameSite) depend on container defaults | Explicit cookie flags at gateway/reverse proxy | SEC-T-014 | Requires Runtime Validation |
| JPET-SEC-015 | Authorization (orders) | `OrderController.viewOrder` L229–234 username check | — | **Control present:** blocks cross-user order view | Preserve in Python ownership checks | SEC-T-015 | Confirmed (control) |
| JPET-SEC-016 | SQL injection | All mapper XML use `#{}` bindings; search keyword wrapped in Java (`CatalogService` L114) | — | Parameterized SQL mitigates classic SQLi | SQLAlchemy bound parameters only | SEC-T-016 | Confirmed (control) |
| JPET-SEC-017 | Mass assignment | `AccountController.newAccount` `@ModelAttribute Account` — no field allowlist; form lacks `status` but POST can add fields | Medium | Attacker adds `status` or other fields to registration POST | DTO allowlist; reject unknown fields | SEC-T-017 | Potential |
| JPET-SEC-018 | Input validation | `NewAccountForm.jsp` — `repeatedPassword` not referenced in Java | Medium | Password mismatch ignored; weak/empty passwords allowed | Validate match, length, complexity in Python | SEC-T-018 | Confirmed |
| JPET-SEC-019 | Business logic | `OrderService.insertOrder` — no stock check; `ItemMapper` decrement without floor | Medium | Order qty &gt; inventory → negative stock; financial/abuse impact in real store | Parity: optional flag; improvement: conditional UPDATE | SEC-T-019 | Confirmed |
| JPET-SEC-020 | Business logic | `OrderController.newOrder` confirm uses session order only; no server-side price recompute at submit | Medium | User manipulates session order object if session tampering possible | Server-side totals from cart lines at submit (Python) | SEC-T-020 | Potential |
| JPET-SEC-021 | Transaction security | `OrderService.insertOrder` `@Transactional` single service | — | **Control present:** atomic rollback on failure within one DB | Single DB transaction + idempotency in Python | SEC-T-021 | Confirmed (control) |
| JPET-SEC-022 | Transaction security | `getNextId` without row lock (`SequenceMapper.xml`, `OrderService` L135–143) | Medium | Concurrent orders: duplicate IDs or lost updates under race | `SELECT … FOR UPDATE` (Python ADR-008) | SEC-T-022 | Potential |
| JPET-SEC-023 | Duplicate orders | No idempotency on confirm POST | Medium | Double-submit places two orders | `Idempotency-Key` (Python ADR-007) | SEC-T-023 | Confirmed |
| JPET-SEC-024 | Rate limiting / DoS | No throttling on login, search, or cart | Medium | Credential stuffing, expensive search loops, cart abuse | Gateway rate limits in Python | SEC-T-024 | Confirmed (gap) |
| JPET-SEC-025 | HTTP security headers | `web.xml`, JSP — no CSP, X-Frame-Options, HSTS | Medium | Clickjacking, MIME sniffing, lack of defense-in-depth for XSS | Security headers at Gateway | SEC-T-025 | Confirmed (gap) |
| JPET-SEC-026 | CORS | Same-origin classic MVC — no CORS headers | — | N/A for legacy browser UI | Restrict CORS in Python API to known origins | SEC-T-026 | N/A legacy |
| JPET-SEC-027 | SSRF | No outbound HTTP client in application code | — | Not applicable | N/A unless Python adds webhooks | SEC-T-027 | N/A |
| JPET-SEC-028 | Open redirect | Controllers use fixed `redirect:/catalog` etc. | — | No user-controlled redirect target found | Validate redirect URLs if added | SEC-T-028 | Confirmed (control) |
| JPET-SEC-029 | Database exposure | `applicationContext.xml` embedded HSQLDB in-process | Low | Misconfigured remote access unlikely; data ephemeral on default embedded | MySQL network isolation in Compose | SEC-T-029 | Confirmed |
| JPET-SEC-030 | Logging / audit | SLF4J simple; no auth/order audit trail | Low | Forensics difficult after incident | Structured JSON logs + security events in Python | SEC-T-030 | Confirmed (gap) |
| JPET-SEC-031 | Backup | No backup/restore in app | — | Missing feature, not vulnerability | Ops process for MySQL | SEC-T-031 | N/A |
| JPET-SEC-032 | Supply chain | `pom.xml` dependencies; `.github/workflows/codeql.yaml` | Medium | Known CVEs in Spring/MyBatis/Tomcat if versions stale | Dependabot, `pip-audit`/Maven equiv, Trivy on images | SEC-T-032 | Requires Runtime Validation |
| JPET-SEC-033 | Docker (legacy) | Java app ships no production Dockerfile in tree | — | Cargo Tomcat for IT only | Trivy scan Python images when built | SEC-T-033 | N/A legacy |
| JPET-SEC-034 | Privilege escalation | No RBAC/admin in codebase | — | No admin escalation path in scope | Do not add admin without approval | SEC-T-034 | N/A |
| JPET-SEC-035 | Access control gap | `editAccountForm` L157–164 — no redirect when unauthenticated | Low | Anonymous user may hit error page or empty form | Redirect to login | SEC-T-035 | Confirmed |
| JPET-SEC-036 | JWT (future) | N/A in Java | — | See `SECURITY_DECISIONS.md` | HS256, short TTL, secret rotation | SEC-T-036 | N/A legacy |

---

## 3. Category notes

### 3.1 Authentication and account security

Legacy authentication is form POST to `/account/signon` with plaintext password verification in SQL (`AccountMapper.getAccountByUsernameAndPassword`). Registration is open (`POST /account/new`). Critical gaps: **JPET-SEC-001**, **JPET-SEC-002**, **JPET-SEC-018**.

### 3.2 Authorization

Order listing/view enforces username match (**JPET-SEC-015**). Account **edit** endpoints fail to bind identity to session (**JPET-SEC-002**, **JPET-SEC-003**).

### 3.3 Password and session management

Passwords stored and compared in plaintext (**JPET-SEC-001**). Session holds `accountBean` and mutable `order`/`cart`. No Spring Security filter chain.

### 3.4 JWT (Python target)

Requirements documented in `SECURITY_DECISIONS.md` §2 — not evaluated on Java codebase.

### 3.5 SQL injection

MyBatis `#{}` parameterization throughout mapper XML; no `${}` string substitution in SQL found. **JPET-SEC-016**.

### 3.6 XSS, CSRF, open redirects

Multiple unescaped JSP EL outputs (**JPET-SEC-007–010**). State-changing GET and unprotected POSTs (**JPET-SEC-004–006**). Fixed server-side redirects only (**JPET-SEC-028**).

### 3.7 SSRF

No server-side URL fetch — **JPET-SEC-027**.

### 3.8 Input validation / mass assignment

Weak registration validation (**JPET-SEC-017**, **JPET-SEC-018**). Checkout merge logic in `OrderController` is field-selective (good) but session-trust model remains (**JPET-SEC-020**).

### 3.9 Sensitive data exposure

Demo credentials in HTML (**JPET-SEC-012**). Payment fields persisted (**JPET-SEC-011**).

### 3.10 Payment security

Demo “fake number” still stored in clear text in DB and shown in JSP (`ViewOrder.jsp` L37).

### 3.11 Business logic

Inventory and duplicate-order issues **JPET-SEC-019**, **JPET-SEC-023**.

### 3.12 Order / inventory transactions

Single-service transaction is correct pattern (**JPET-SEC-021**); concurrency weaknesses **JPET-SEC-022**.

### 3.13 Rate limiting / DoS

**JPET-SEC-024** — missing control, abuse exposure in production.

### 3.14 CORS / headers

Legacy same-origin; Python must set explicit CORS and headers (**JPET-SEC-025**, **JPET-SEC-026**).

### 3.15 Docker / infrastructure

Legacy: Cargo/Tomcat for tests. Python Compose must not publish MySQL or internal APIs (**TARGET_ARCHITECTURE**).

### 3.16 Supply chain

Maven BOM; CodeQL workflow present on upstream project. Run dependency CVE scan on pinned versions (**JPET-SEC-032**).

### 3.17 Logging / monitoring

Minimal application security logging (**JPET-SEC-030**).

### 3.18 Backup / DB access

Operational, not implemented in app (**JPET-SEC-031**).

---

## 4. Tool suitability (Python + legacy)

| Tool | Suitability | Use in this program |
|------|-------------|---------------------|
| **Bandit** | High for Python | SAST: hardcoded secrets, unsafe APIs, SQL formatting mistakes |
| **Semgrep** | High | Custom rules: JWT validation, missing auth deps, logging leaks |
| **pip-audit** | High | CI gate on Python dependencies |
| **OWASP ZAP** | High (runtime) | Baseline scan on Gateway after Compose up; CSRF/XSS/header checks |
| **Trivy** | High | Scan Python service images and `mysql:8` base |
| **Gitleaks** | High | Prevent committed `.env`, JWT secrets, seed passwords |
| **pytest** | High | Security unit/integration tests in `SECURITY_TEST_CASES.md` |

Legacy Java: existing **CodeQL** workflow in `jpetstore-6/.github/workflows/codeql.yaml` complements but does not replace manual findings above.

---

## 5. Python application security requirements (summary)

Full normative list: `SECURITY_DECISIONS.md`. Highlights:

- JWT validation at Gateway; short-lived access tokens; `sub` = username  
- Bcrypt (or Argon2) password hashing  
- Centralized authorization: every mutating route checks identity + ownership  
- SQLAlchemy 2 parameterized queries only  
- Pydantic input models (allowlist fields)  
- Rate limiting on `/auth/login`, `/orders`, search  
- Secrets via environment; `JWT_SECRET` ≥ 32 bytes  
- Payment field minimization + log redaction  
- Order transaction atomicity + `Idempotency-Key`  
- Security headers + restrictive CORS  
- `pip-audit`, Bandit, Semgrep, Trivy, Gitleaks in CI  
- Structured logging with redaction filters  

---

## 6. Executive security summary

JPetStore 6 is a **demonstration application**, not a hardened production system. The review **confirmed critical weaknesses**: **plaintext passwords**, **unauthenticated account profile updates**, and **missing CSRF protections** on checkout. **Stored XSS** is practical via registrable profile fields rendered unsafely in JSP. **Order authorization** for view-by-id is implemented correctly; **SQL injection** risk is low due to MyBatis parameter binding.

The Python target architecture should **not replicate** session-trust and plaintext patterns. Intentional improvements (JWT, bcrypt, idempotency, rate limits, headers) are required; parity items (demo card storage, negative inventory) need explicit acceptance in `SECURITY_RISK_REGISTER.md`.

---

## 7. Critical and high-risk findings

| ID | Title |
|----|--------|
| JPET-SEC-001 | Plaintext password storage and authentication |
| JPET-SEC-002 | Unauthenticated account update via POST `/account/edit` |
| JPET-SEC-003 | Account update IDOR via tampered `username` |
| JPET-SEC-004 | CSRF on order confirmation |
| JPET-SEC-007 | Stored XSS via profile `firstName` in welcome message |
| JPET-SEC-011 | Payment card data stored and displayed from database |

---

## 8. Confirmed vs unverified

| Status | Count | IDs |
|--------|-------|-----|
| **Confirmed** | 24 | JPET-SEC-001–012, 015–016, 018–019, 021, 023–025, 028–030, 035 |
| **Potential** | 5 | JPET-SEC-010, 013, 017, 020, 022 |
| **Requires Runtime Validation** | 2 | JPET-SEC-014, 032 |
| **Controls / N/A** | 5 | JPET-SEC-015, 016, 021, 026–028, 031, 033–034, 036 |

---

## 9. Security controls required in Python (before release)

See §5 and `SECURITY_REMEDIATION_PLAN.md` Phase 1–3. Minimum bar: fix authz model (**002/003**), password hashing (**001**), CSRF not applicable to pure JSON API with JWT (use CORS + no cookies for auth), XSS via JSON + encoded UI, idempotency (**023**), rate limits (**024**), headers (**025**), dependency/container scans (**032**).

---

## 10. Automated tests required before release

Full catalog: `SECURITY_TEST_CASES.md`. P0: SEC-T-002, SEC-T-003, SEC-T-004, SEC-T-007, SEC-T-011, SEC-T-015, SEC-T-021, SEC-T-023.

---

## 11. Remaining accepted risks (legacy parity)

Documented in `SECURITY_RISK_REGISTER.md`: demo PAN storage, negative inventory, duplicate search results, no admin RBAC.

---

**Assessment complete — await review before Python backend implementation.**
