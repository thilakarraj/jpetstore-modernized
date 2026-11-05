# JPetStore Python Security Decisions --- Modular Monolith

## 1. Normative decisions

  -----------------------------------------------------------------------
  ID                      Topic                   Decision
  ----------------------- ----------------------- -----------------------
  SEC-D-01                Authentication          JWT bearer access token
                                                  validated by FastAPI

  SEC-D-02                Password storage        Bcrypt; tune work
                                                  factor for deployment

  SEC-D-03                Authorization           Central FastAPI
                                                  dependencies plus
                                                  service-level ownership
                                                  checks

  SEC-D-04                Account updates         Identity from
                                                  authenticated JWT
                                                  `sub`; never trust body
                                                  username

  SEC-D-05                Registration            Return success without
                                                  automatically issuing
                                                  JWT (functional parity)

  SEC-D-06                SQL                     SQLAlchemy ORM/Core
                                                  with bound parameters
                                                  only

  SEC-D-07                Input                   Pydantic write DTOs;
                                                  reject unknown fields

  SEC-D-08                Output                  JSON API; UI safely
                                                  renders untrusted
                                                  strings

  SEC-D-09                CSRF                    Bearer token in
                                                  Authorization header;
                                                  if cookies added,
                                                  require CSRF tokens

  SEC-D-10                CORS                    Explicit
                                                  frontend-origin
                                                  allowlist

  SEC-D-11                Rate limiting           Login, registration,
                                                  search and order
                                                  submission

  SEC-D-12                Secrets                 Environment/secret
                                                  manager; `.env`
                                                  local-only and
                                                  gitignored

  SEC-D-13                Payment                 Synthetic payment only;
                                                  never store CVV or full
                                                  PAN

  SEC-D-14                Orders                  One DB transaction;
                                                  required
                                                  Idempotency-Key

  SEC-D-15                Inventory               Preserve
                                                  negative-inventory
                                                  parity by default;
                                                  document risk

  SEC-D-16                Architecture            One FastAPI app, one
                                                  MySQL database/schema;
                                                  no Gateway or internal
                                                  identity header

  SEC-D-17                Headers                 nosniff, frame
                                                  protection, referrer
                                                  policy, CSP; HSTS only
                                                  on HTTPS

  SEC-D-18                Logging                 Structured logs; redact
                                                  passwords, tokens,
                                                  Authorization and
                                                  payment data

  SEC-D-19                Supply chain            pip-audit, Bandit,
                                                  Semgrep, Trivy,
                                                  Gitleaks

  SEC-D-20                RBAC/Admin              Do not implement
                                                  without explicit
                                                  approval
  -----------------------------------------------------------------------

## 2. JWT

Use HS256 for the assessment and explicitly allow only HS256. Require
`sub`, `iat`, `exp`, `iss` and `aud`. Validate signature, expiry,
issuer, audience and non-empty subject. Reject `alg=none`, malformed and
tampered tokens. Use a strong secret of at least 32 bytes and a
configurable short access-token TTL (default 60 minutes).

FastAPI validates the token directly. There is no Gateway and no
`X-User-Id` forwarding. Registration does not issue a token. Client-side
logout deletes the in-memory token but does not revoke a copied token;
document this limitation.

## 3. Passwords and authorization

Hash passwords with bcrypt. Never store/log/return plaintext passwords
or hashes. Seed `j2ee` and `ACID` only in local/test environments, as
hashes; disable demo credentials in production-like environments.

-   `GET/PUT /account/me`: authenticated user only.
-   `GET /orders`: filter by authenticated `sub`.
-   `GET /orders/{id}`: verify order owner equals `sub`.
-   `POST /orders`: derive user identity from `sub`, never request body.
-   Guest cart: random opaque cart ID; authenticated cart bound to user.
-   Catalog reads: public.
-   No admin, role or permission assignment fields.

## 4. SQL, validation and output

Use SQLAlchemy bound parameters. Prohibit user-controlled SQL string
concatenation/f-strings. Use explicit Pydantic write DTOs with
`extra="forbid"`. Validate lengths, numeric bounds, enums and request
size. Never trust client-supplied prices, totals, user IDs, status or
inventory values.

API returns JSON. Product descriptions and banners are untrusted text.
Frontend must not inject them as raw HTML. If rich HTML is required
later, use an allowlist sanitizer and a new decision.

## 5. CSRF, CORS and headers

Bearer tokens explicitly supplied in Authorization headers reduce
conventional CSRF exposure. Do not use ambient auth cookies for the
assessment SPA. If cookie auth is introduced, require Secure, HttpOnly,
SameSite and CSRF tokens. CORS is not authorization.

Use explicit CORS origins and only required methods/headers. Never
combine wildcard origin with credentials. Add nosniff, frame protection,
referrer policy and CSP. Enable HSTS only over HTTPS.

## 6. Rate limits and secrets

Rate-limit login, registration, search and order submission; return 429
and Retry-After. If deployment runs multiple instances, do not assume
in-memory limits are globally shared.

Inject secrets via environment/deployment secret manager. Commit
`.env.example` placeholders only. Use a least-privilege MySQL
application user. Do not expose MySQL publicly. Run migrations as a
controlled deployment step; never run seeders in production.

## 7. Payment minimization

Use synthetic payment data only. Never collect/store CVV or full PAN.
Legacy card columns, if present in source schema, should be unused or
removed from the Python target schema with the migration documented.
Never log payment details. The assessment is not PCI DSS compliant.

## 8. Atomic order and idempotency

Within one SQLAlchemy transaction: validate user/cart; check
`(user_id, idempotency_key)`; return prior result if completed; lock
sequence row; retrieve authoritative item prices; compute totals
server-side; apply accepted inventory behavior; insert
order/status/lines; persist idempotency result in the same transaction;
clear/mark cart; commit. Add a unique constraint and handle concurrent
duplicate-key races.

## 9. CI and logging

Run pip-audit, Bandit, Semgrep, Gitleaks and Trivy. Pin dependencies and
review findings. JSON logs may include request ID, route, status and
duration. Redact password/hash, Authorization, JWT, database secrets and
payment data. Record login success/failure, authorization denial and
order creation without sensitive payloads.

## 10. Parity vs improvement

  -----------------------------------------------------------------------
  Legacy behavior                     Python stance
  ----------------------------------- -----------------------------------
  Plaintext passwords                 Fix with bcrypt

  Unauthenticated account edit / IDOR Fix

  CSRF-prone form actions             Bearer-token JSON API

  Stored XSS in JSP                   Safe data handling and UI rendering

  Negative inventory                  Preserve by default; accepted risk

  Card data persistence               Replace with synthetic payment
                                      reference; no PAN/CVV

  No idempotency                      Add

  No rate limiting                    Add

  No formal RBAC                      Do not invent
  -----------------------------------------------------------------------

## 11. Approval

  Role                       Name   Date   Approval
  -------------------------- ------ ------ ----------
  Architecture                             
  Engineering                              
  Security reviewer                        
  Product/assessment owner                 
