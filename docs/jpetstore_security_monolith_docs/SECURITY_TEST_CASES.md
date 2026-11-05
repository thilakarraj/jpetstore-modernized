# JPetStore Security Test Cases --- Modular Monolith

Automated tests use pytest unless marked manual. Existing IDs are
retained. `BASE` is the FastAPI URL,
e.g. `http://localhost:8000/api/v1`; configure the actual port. There is
no Gateway.

P0 = release blocker; P1 = pre-production; P2 = recommended.

  --------------------------------------------------------------------------------------
  Test ID                 Priority                Test and expected result
  ----------------------- ----------------------- --------------------------------------
  SEC-T-001               P0                      Register, inspect DB and login: bcrypt
                                                  hash only; wrong password returns 401.

  SEC-T-002               P0                      `PUT /account/me` without JWT returns
                                                  401; DB unchanged.

  SEC-T-003               P0                      User A cannot update B by supplying
                                                  B's username/user ID; identity comes
                                                  from JWT `sub`.

  SEC-T-004               P0                      `POST /orders` without JWT returns
                                                  401; no state changes.

  SEC-T-005               P1                      Cart mutations use POST/PUT/DELETE;
                                                  guest cart IDs are unguessable;
                                                  cross-user cart access is
                                                  denied/isolated.

  SEC-T-006               P2                      After token removal, protected route
                                                  returns 401; document that client
                                                  deletion is not server revocation.

  SEC-T-007               P0                      Script-like profile value is returned
                                                  as JSON text and never executes in UI.

  SEC-T-008               P1                      Banner content is URL/text or strictly
                                                  sanitized; arbitrary script does not
                                                  execute.

  SEC-T-009               P1                      Product descriptions are data; UI does
                                                  not inject untrusted HTML.

  SEC-T-010               P2                      Search/error input is not reflected as
                                                  executable HTML; no stack trace
                                                  leakage.

  SEC-T-011               P0                      Synthetic payment fixture only; no
                                                  CVV/full PAN in DB, API or logs.

  SEC-T-012               P2                      Demo credentials absent/disabled in
                                                  production-like environment.

  SEC-T-013               P2                      Legacy manual session-fixation test
                                                  optional; Python bearer-only API has
                                                  no login session.

  SEC-T-014               P2                      No auth cookie expected; if cookies
                                                  introduced, verify
                                                  Secure/HttpOnly/SameSite and CSRF.

  SEC-T-015               P0                      User A cannot retrieve User B's order;
                                                  return 403/404 per API policy.

  SEC-T-016               P0                      SQL injection payloads are treated as
                                                  literal input; no SQL error leakage.

  SEC-T-017               P1                      `role`, `is_admin`, `user_id`,
                                                  `status` mass assignment
                                                  rejected/ignored; no privilege change.

  SEC-T-018               P1                      Too-short/long password or mismatched
                                                  confirmation rejected.

  SEC-T-019               P1                      Order quantity exceeding stock follows
                                                  approved parity mode; strict mode
                                                  requires a separate decision.

  SEC-T-020               P1                      Client-tampered prices/totals ignored;
                                                  server computes authoritative totals.

  SEC-T-021               P0                      Inject failure during order creation;
                                                  order, inventory, sequence and
                                                  idempotency changes all roll back.

  SEC-T-022               P2                      Concurrent distinct orders receive
                                                  unique order IDs.

  SEC-T-023               P0                      Same user/key repeated or concurrent:
                                                  exactly one order and one inventory
                                                  decrement; return stored result or
                                                  documented conflict.

  SEC-T-024               P1                      Login/register/search/order thresholds
                                                  return 429 and Retry-After.

  SEC-T-025               P1                      Responses contain nosniff, frame
                                                  protection, referrer policy and CSP;
                                                  HSTS only on HTTPS.

  SEC-T-026               P1                      Untrusted CORS origin receives no
                                                  allow-origin; no wildcard with
                                                  credentials.

  SEC-T-027               P2                      SSRF N/A unless outbound URL fetching
                                                  is added; then test
                                                  loopback/private/link-local/metadata
                                                  addresses.

  SEC-T-028               P2                      Redirect targets are fixed or
                                                  allowlisted; external redirect payload
                                                  rejected.

  SEC-T-029               P1                      MySQL is not publicly exposed; app DB
                                                  user has least privilege.

  SEC-T-030               P1                      Logs contain no password/hash, JWT,
                                                  Authorization header, CVV or full PAN.

  SEC-T-031               P2                      Backup/restore runbook exists and
                                                  restore succeeds in isolated
                                                  environment.

  SEC-T-032               P1                      pip-audit and SAST run in CI;
                                                  Critical/High findings have documented
                                                  disposition.

  SEC-T-033               P1                      Trivy image scan reviewed; no
                                                  unresolved Critical; container runs
                                                  non-root.

  SEC-T-034               P0 process              No admin routes/role assignment
                                                  without explicit approval.

  SEC-T-035               P1                      `GET /account/me` without JWT returns
                                                  401.

  SEC-T-036               P0                      Expired, tampered, `alg=none`, wrong
                                                  issuer/audience or missing-sub JWT
                                                  returns 401.
  --------------------------------------------------------------------------------------

## Release gate

-   [ ] All P0 pytest tests green.
-   [ ] P1 tests for exposed routes green before production-like
    deployment.
-   [ ] Bandit, pip-audit, Semgrep reviewed.
-   [ ] Trivy reviewed.
-   [ ] Gitleaks clean.
-   [ ] ZAP baseline reviewed; no unresolved High findings on auth/order
    flows.
-   [ ] CORS, TLS and headers verified on deployed environment.
-   [ ] Risk register reviewed and approved.
