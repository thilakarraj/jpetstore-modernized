# Security Implementation (Phase 3)

Assessment reference: `../../docs/SECURITY_DECISIONS.md`.

## Phase 1–2 (retained)

- Security headers middleware
- Log redaction (`RedactingFilter`)
- Optional Prometheus basic auth

## Passwords (SEC-D-02)

- Bcrypt via `jpetstore.security.passwords` (12 rounds)
- Plaintext never stored or returned
- Seed/demo credentials documented in `DEV_CREDENTIALS.md` only

## JWT (SEC-D-01)

- Library: `python-jose`
- Algorithm: `HS256` (configurable via `JWT_ALGORITHM`)
- Claims: `sub` (username), `iss`, `aud`, `iat`, `exp` only
- Secret: `JWT_SECRET` environment variable (never hardcoded)
- Validation on protected routes via `get_current_user` dependency
- Identity for authorization comes from validated `sub`, never from request body

## Authorization (SEC-D-04)

- `GET/PUT /api/v1/account/me` require valid Bearer JWT
- No route to read or update another user by ID (IDOR surface removed vs legacy JSP)
- Profile update schema excludes username and internal identifiers (mass assignment control)

## Rate limiting (SEC-D-11, ADR-P3-001)

- In-process fixed-window limiter (`jpetstore.core.rate_limit`)
- Applied to `POST /auth/login` and `POST /auth/register`
- Keys: client IP + endpoint class
- HTTP **429** with `RATE_LIMIT_EXCEEDED`
- **Limitations:** not shared across workers/replicas; counters reset on restart; NAT may bucket many clients

## Audit logging

Logger: `jpetstore.security` → `security-audit.log`

Events include: `auth.register`, `auth.login`, `auth.token`, `auth.rate_limit`, `account.read`, `account.update`.

Each record includes timestamp, `request_id`, `event`, `outcome`, optional `user_identifier`, route/method when set.

**Never logged:** passwords, hashes, JWTs, `Authorization` headers, full request bodies.

## Login errors

Same message for unknown user and bad password (no username enumeration via message text).

## Cart (Phase 5)

- All `/api/v1/cart/**` routes require valid JWT.
- Cart ownership enforced by `userid` from JWT `sub` in service/repository (no cart id from client for ownership).
- Strict Pydantic schemas — no client prices, totals, or user id fields.
- Quantities must be positive integers (DB check + API validation).
- Security audit events: `cart.add`, `cart.read`, `cart.update`, `cart.remove`, `cart.clear`.
- Prometheus: `cart_add_total`, `cart_update_total`, `cart_remove_total` with `outcome` label only.

## Orders / checkout (Phase 6)

- `POST /api/v1/orders/checkout` requires JWT + `Idempotency-Key`.
- Ownership: `orders.userid` must match JWT `sub` for read APIs.
- Payment: only last-four + type + expiry accepted; stored masked; never log payment fields.
- Audit: `order.checkout`, `order.list`, `order.read`, `order.idempotency`, `order.inventory`.
- Metrics: `orders_created_total{outcome}` (existing counter).
