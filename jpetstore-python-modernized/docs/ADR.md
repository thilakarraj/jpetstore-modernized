# ADR — Project-local decisions

## ADR-P1-001 Modular monolith

Single FastAPI process and single MySQL schema (per assessment update).

## ADR-P1-002 Phase 1 operational surface

Only health and metrics endpoints until business modules land.

## ADR-P1-003 SQLite in unit tests

In-memory SQLite for pytest; production uses MySQL 8.

## ADR SEC-P2-001 Wider signon.password column

Legacy `VARCHAR(25)` cannot store bcrypt hashes. Migration uses `VARCHAR(255)` per `SECURITY_DECISIONS.md` SEC-D-02. **Behavior change:** storage format only; login semantics unchanged after seed.

## ADR-P3-001 In-memory authentication rate limiting

**Context:** SEC-D-11 requires login/register throttling; Redis/Kubernetes are out of scope (AI_GUARDRAILS).  
**Decision:** Fixed-window counters per client IP in process memory (`jpetstore.core.rate_limit`).  
**Consequences:** Effective per replica; not suitable as sole defense for large distributed deployments without a shared store (future ADR if needed).

## ADR-P3-002 JWT validation in monolith

**Context:** Assessment SEC-D-03 describes Gateway-trust headers for microservices.  
**Decision:** Modular monolith validates Bearer JWT on protected routes locally (`modules/account/dependencies.py`).  
**Consequences:** No `X-User-Id` trust boundary; aligns with single-process deployment.

## ADR-P5-001 Persistent database-backed cart

**Context:** Legacy JPetStore keeps the cart in HTTP session (FR-2.1). The modernized API uses JWT, not server sessions, and must support restarts and multiple app instances.

**Decision:**

- Store carts in new tables `cart` and `cart_item` (migration `0003_phase5_cart`).
- One cart row per authenticated user (`UNIQUE(userid)`), status `active` (checkout will use `checked_out` in a later phase).
- `cart.userid` → FK `account.userid` with `ON DELETE CASCADE`.
- `cart_item.itemid` → FK `item.itemid`; unique `(cart_id, itemid)`; check `quantity > 0`.
- Persist **item id + quantity only** — never client-supplied prices or totals.
- Prices and subtotals are computed on read from current catalog `item.listprice` using `Decimal`.
- Cart operations do **not** reserve or decrement inventory; `in_stock` is informational from current `inventory.qty`.
- Checkout, orders, and payment remain out of scope for Phase 5.

**Concurrency:** Cart and line creation use SQLAlchemy `begin_nested()` SAVEPOINTs; duplicate insert under race resolves by re-reading the row and merging quantity (unique constraints).

**Unavailable catalog items:** Lines remain in the cart with `item_available: false` and null pricing until removed by the user.

## ADR-P6-001 Inventory non-negative (change from legacy)

**Context:** Legacy allows negative inventory (SEC-D-15 parity). Phase 6 checkout must not oversell.  
**Decision:** Reject checkout when `inventory.qty` &lt; required quantity; decrement in the same transaction. MySQL migration adds `CHECK (qty >= 0)`; ORM model includes the check for SQLite tests.  
**Consequences:** **Behavior change** vs legacy demo; prevents overselling.

## ADR-P6-002 Synthetic payment only

**Context:** No payment gateway in scope; assessment demo stored full PAN.  
**Decision:** Checkout accepts `card_type`, `card_last_four`, `expiry_date` only — **no CVV field** in API. Persist masked `****{last4}` in `orders.creditcard`. Synthetic validation of card type enum only.  
**Consequences:** Not PCI compliant; no real payment processing.

## ADR-P6-003 Checkout idempotency

**Context:** SEC-D / API spec require `Idempotency-Key`.  
**Decision:** Table `checkout_idempotency` with `UNIQUE(userid, idempotency_key)`, SHA-256 request fingerprint, `orderid` set on success. Same key + same body → replay order (HTTP 200); same key + different body → HTTP 409. Row locked with `SELECT … FOR UPDATE` during checkout.  
**Retention:** Keys retained indefinitely in Phase 6 (ops cleanup deferred).

## ADR-P6-004 Atomic checkout transaction

**Context:** FR-4.5 requires order + status + lines + inventory + cart clear atomically.  
**Decision:** Single DB transaction: idempotency row → lock cart → validate lines/prices → lock `sequence` row → insert order/status/lines → lock/decrement inventory → mark cart `checked_out` → attach `orderid` to idempotency → commit. Failure rolls back all effects.

## ADR-P6-005 Cart lifecycle at checkout

**Context:** ADR-P5-001 one cart row per user.  
**Decision:** On success set `cart.status = checked_out` and delete line rows. Next cart operation reactivates the same row to `active` (empty).

## ADR-P6-006 Row locking (MySQL)

**Context:** Concurrent checkout must not double-allocate sequence or oversell.  
**Decision:** `with_for_update()` on idempotency (when present), cart, `sequence`, and each `inventory` row during decrement. **SQLite tests** do not enforce MySQL row locks; MySQL integration validation recommended for lock semantics.
