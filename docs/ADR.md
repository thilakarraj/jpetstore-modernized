# Architecture Decision Records (ADR)

**Project:** JPetStore Python modernization  
**Format:** MADR-style summaries

---

## ADR-001: Four-service decomposition with API Gateway

**Status:** Accepted  
**Context:** Legacy monolith (`jpetstore-6`) combines catalog, account, cart, and order in one WAR. Target requires Catalog, Account, Order services plus Gateway.  
**Decision:** Split into Gateway + Catalog + Account + Order FastAPI apps. Gateway is the only public entrypoint.  
**Consequences:** Sync HTTP between services; operational overhead of four containers—acceptable for assessment. No Kubernetes.

---

## ADR-002: Single MySQL server, three schemas

**Status:** Accepted  
**Context:** Legacy uses one embedded HSQLDB. Full database-per-service with separate servers is unnecessary for assessment.  
**Decision:** One MySQL 8 container; schemas `jpetstore_catalog`, `jpetstore_account`, `jpetstore_order`. No cross-schema foreign keys.  
**Consequences:** Simpler Compose and backups; services must not join across schemas in SQL.

---

## ADR-003: Order Service owns inventory and order transactions

**Status:** Accepted  
**Context:** TR-4.1 requires atomic sequence + inventory + order + lineitem + orderstatus in one transaction.  
**Decision:** All mutable inventory and order tables live in `jpetstore_order`. Catalog reads qty via Order internal API.  
**Consequences:** Extra HTTP hop for item detail `in_stock`; catalog availability depends on Order Service for reads.

**Alternatives rejected:** Split inventory with 2PC or Saga—too heavy for scope.

---

## ADR-004: JWT authentication (intentional improvement)

**Status:** Accepted  
**Context:** Legacy uses HTTP session (`accountBean`). Target requires JWT and password hashing.  
**Decision:** Account Service issues HS256 JWT; Gateway validates; downstream services trust `X-User-Id` from Gateway on internal network.  
**Consequences:** Stateless auth; logout is client-side; FR-3.6 preserved by omitting token on register.

**Parity note:** Not session-compatible with legacy Selenide tests without test harness changes.

---

## ADR-005: Password hashing with bcrypt

**Status:** Accepted  
**Context:** TR-5.3 plaintext passwords in legacy.  
**Decision:** Store bcrypt hash in `signon.password`; seed script hashes `j2ee`/`ACID` passwords for dev.  
**Consequences:** Improved security; migration must re-seed or hash on first login if importing legacy DB.

---

## ADR-006: Cart and checkout state in Order Service database

**Status:** Accepted  
**Context:** Legacy cart and partial order in HTTP session (FR-2.1, multi-step checkout).  
**Decision:** Tables `cart`, `cart_line`, `checkout_draft` in order schema; guest carts keyed by `X-Cart-Id`.  
**Consequences:** No Redis; horizontal scaling needs sticky cart id or login—out of assessment scope.

---

## ADR-007: Idempotency keys on order creation

**Status:** Accepted  
**Context:** Duplicate POST on confirm could double-charge inventory (legacy had same race).  
**Decision:** Require `Idempotency-Key` on `POST /orders`; persist response in `idempotency_key` table within same transaction as order or immediately after success.  
**Consequences:** **Improvement** over legacy; clients must generate UUID once per checkout attempt.

---

## ADR-008: Sequence allocation with row lock

**Status:** Accepted  
**Context:** Legacy `getNextId` read/update without `FOR UPDATE` (TR-4.1 concurrency gap).  
**Decision:** `SELECT ... FOR UPDATE` on `sequence` row inside order transaction; increment before commit.  
**Consequences:** Safer IDs under concurrency; still single-row bottleneck—acceptable for demo load.

---

## ADR-009: Preserve legacy order quirks for behavioral parity

**Status:** Accepted  
**Context:** TR-6.1–TR-6.4 document negative inventory, no submit-time stock check, duplicate search, `orderstatus.linenum`.  
**Decision:** Do not add stock checks at order submit; allow negative `inventory.qty`; keep duplicate search union; insert orderstatus with `linenum = order_id`.  
**Consequences:** Parity with demo behavior; document in API spec as known limitations.

**Future ADR:** Non-negative inventory flag—only if product approves breaking parity.

---

## ADR-010: Sync HTTP only (no Kafka)

**Status:** Accepted  
**Context:** Constraint forbids Kafka.  
**Decision:** Order → Catalog/Account via `httpx` with timeouts and circuit-breaker-lite (fail fast after N errors).  
**Consequences:** Cascading failures possible; readiness checks exclude degraded optional paths where defined.

---

## ADR-011: FastAPI Gateway with httpx proxy

**Status:** Accepted  
**Context:** Team standard FastAPI; avoid introducing nginx config as second language unless needed.  
**Decision:** Python Gateway validates JWT and reverse-proxies to services.  
**Consequences:** Can swap to nginx later without API contract change.

---

## ADR-012: Structured JSON logging

**Status:** Accepted  
**Context:** TR-8.1 minimal logging in legacy.  
**Decision:** All services use shared `jpetstore_common.logging` JSON formatter; propagate `X-Request-Id`.  
**Consequences:** Easy ingestion; must enforce no PCI/password in logs (see AI_GUARDRAILS.md).

---

## ADR-013: pytest + Compose for integration tests

**Status:** Accepted  
**Context:** Assessment deadline; need TR-4.1 verification.  
**Decision:** `docker compose -f docker-compose.test.yml up` for CI/local e2e; pytest per service with transactional rollbacks where possible.  
**Consequences:** Slower tests than unit-only; required for inventory rollback test.

---

## ADR-014: Credit card storage parity

**Status:** Accepted  
**Context:** FR-4.5 persists card on order row (demo).  
**Decision:** Continue storing `credit_card`, `exprdate`, `cardtype` on `orders` table; mask in logs.  
**Consequences:** Not PCI compliant—acceptable for sample app only.

---

## Decision log (pending)

| ID | Topic | Trigger to revisit |
|----|-------|-------------------|
| ADR-P1 | Guest cart merge on login | UX requirement |
| ADR-P2 | BFF HTML UI vs SPA | UI phase |
| ADR-P3 | Read-only inventory cache in Catalog | Order read load |
