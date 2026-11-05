# JPetStore 6 Security Assessment --- Modular Monolith

**Review date:** 2026-11-04\
**Review type:** Static review of the supplied Java/JSP/MyBatis/Spring
source analysis. No dynamic penetration test has been executed.\
**Target:** Python 3.12+, FastAPI modular monolith, SQLAlchemy 2, MySQL
8, Alembic and Docker Compose.

## 1. Target architecture

The Python application is one deployable FastAPI application with
logically separated Account, Catalog, Cart and Order modules, using one
MySQL database and one application schema. FastAPI validates JWTs
directly. There is no API Gateway, no inter-service HTTP boundary, and
no trusted `X-User-Id` header.

## 2. Finding status

-   **Confirmed:** direct source evidence supports the finding.
-   **Potential:** source suggests a weakness; exploitability needs
    further validation.
-   **Requires Runtime Validation:** deployment/container behavior must
    be checked.
-   **Control / N/A:** a control exists or the issue does not apply to
    the reviewed legacy application.

## 3. Legacy finding register

  --------------------------------------------------------------------------------------
  ID             Finding                 Severity       Status         Python target
                                                                       action
  -------------- ----------------------- -------------- -------------- -----------------
  JPET-SEC-001   Plaintext password      Critical       Confirmed      Bcrypt hashes;
                 storage/comparison                                    never log
                                                                       plaintext

  JPET-SEC-002   Unauthenticated account Critical       Confirmed      Authenticated
                 update                                                principal
                                                                       required

  JPET-SEC-003   Account IDOR via client High           Confirmed      Identity from JWT
                 username                                              `sub` only

  JPET-SEC-004   CSRF on order           High           Confirmed      Bearer-token JSON
                 confirmation                                          API; no ambient
                                                                       auth cookie

  JPET-SEC-005   State-changing cart GET Medium         Confirmed      POST/PUT/DELETE
                 actions                                               mutations

  JPET-SEC-006   GET logout can be       Low            Confirmed      POST logout if
                 CSRF-triggered                                        endpoint exists

  JPET-SEC-007   Stored XSS via profile  High           Confirmed      Safe text
                 first name                                            handling and UI
                                                                       rendering

  JPET-SEC-008   Banner HTML rendered    Medium         Confirmed      URL/text or
                 without safe handling                                 strict
                                                                       sanitization

  JPET-SEC-009   Product descriptions    Medium         Confirmed      API data only;
                 rendered as HTML                                      safe UI rendering

  JPET-SEC-010   Potential reflected XSS Low            Potential      Controlled
                 in message output                                     messages and
                                                                       output encoding

  JPET-SEC-011   Payment fields          High           Confirmed      Synthetic payment
                 persisted/displayed                                   only; no CVV/full
                                                                       PAN

  JPET-SEC-012   Demo credentials        Low            Confirmed      Local/test only
                 prefilled in sign-in                                  
                 page                                                  

  JPET-SEC-013   Session fixation        Medium         Potential      Bearer-only API;
                 concern at login                                      review if
                                                                       sessions added

  JPET-SEC-014   Session cookie flags    Medium         Requires       Not applicable
                 not explicit                           Runtime        unless cookies
                                                        Validation     introduced

  JPET-SEC-015   Order view checks owner ---            Control        Preserve
                                                        present        ownership checks

  JPET-SEC-016   MyBatis uses bound      ---            Control        SQLAlchemy bound
                 parameters                             present        parameters only

  JPET-SEC-017   Account model binding   Medium         Potential      Pydantic write
                 lacks field allowlist                                 DTO allowlist;
                                                                       reject extras

  JPET-SEC-018   Password                Medium         Confirmed      Validate
                 confirmation/strength                                 confirmation and
                 validation weak                                       length

  JPET-SEC-019   Inventory may become    Medium         Confirmed      Preserve accepted
                 negative                                              parity; document
                                                                       risk

  JPET-SEC-020   Checkout trusts session Medium         Potential      Recompute
                 order state                                           prices/totals
                                                                       server-side

  JPET-SEC-021   Legacy order service is ---            Control        Preserve atomic
                 transactional                          present        transaction

  JPET-SEC-022   Sequence lacks explicit Medium         Potential      Lock sequence row
                 row lock                                              in transaction

  JPET-SEC-023   No order idempotency    Medium         Confirmed      Atomic
                                                                       idempotency
                                                                       key/result

  JPET-SEC-024   No login/search/cart    Medium         Confirmed gap  Rate-limit
                 throttling                                            sensitive
                                                                       endpoints

  JPET-SEC-025   Security headers not    Medium         Confirmed gap  Add CSP, nosniff,
                 identified                                            frame protection;
                                                                       HSTS on HTTPS

  JPET-SEC-026   Legacy same-origin app  ---            N/A legacy     Explicit
                 has no CORS policy                                    allowlist for SPA
                                                                       deployment

  JPET-SEC-027   No server-side URL      ---            N/A            Reassess if URL
                 fetching identified                                   fetching added

  JPET-SEC-028   Fixed redirects found   ---            Control        Keep fixed or
                                                        present        allowlisted

  JPET-SEC-029   Legacy default uses     Low            Confirmed      Keep MySQL
                 embedded HSQLDB                        observation    private

  JPET-SEC-030   Minimal security audit  Low            Confirmed gap  Structured logs
                 logging                                               and redaction

  JPET-SEC-031   No backup/restore       ---            Operational    Document and test
                 runbook                                gap            backup/restore

  JPET-SEC-032   Dependency versions     Medium         Requires       pip-audit and
                 need current scan                      Runtime        dependency
                                                        Validation     scanning

  JPET-SEC-033   No production           ---            N/A legacy     Scan Python
                 Dockerfile identified                                 image; non-root
                 in legacy tree                                        runtime

  JPET-SEC-034   No formal RBAC/admin    ---            N/A            Do not add
                 identified                                            without approval

  JPET-SEC-035   Account edit form lacks Low            Confirmed      Protect
                 robust unauthenticated                                `/account/me`
                 handling                                              

  JPET-SEC-036   JWT not present in      ---            N/A legacy     Strict JWT
                 legacy app                                            validation in
                                                                       FastAPI
  --------------------------------------------------------------------------------------

The supplied assessment records 24 confirmed findings, 5 potential
findings and 2 requiring runtime validation. Use the per-finding
classifications above as the detailed register.

## 4. Additional target checks

These are target requirements, not claims of confirmed legacy
vulnerabilities:

-   JWT issuer, audience, expiry and algorithm validation.
-   Account enumeration and login/register throttling.
-   Request body size and pagination limits.
-   Mass assignment and protected-field tampering.
-   Concurrent order/idempotency race conditions.
-   MySQL least privilege and network isolation.
-   Non-root container and secret scanning.
-   Health endpoint information disclosure.
-   Safe exception handling and log redaction.
-   Backup access controls and restore validation.
-   TLS and deployment secret configuration.

## 5. Release gates

Before public assessment demo: P0 tests pass; no real payment data; no
secrets in Git/logs; DB not public; CORS restricted;
JWT/ownership/transaction/idempotency tests pass; accepted risks
documented.

Before production-like deployment: P0/P1 tests pass; ZAP baseline
reviewed; container/dependency scans reviewed; rate limits, TLS, headers
and backup/restore verified.

## 6. Limitations

This is a static review, not a penetration test. Potential findings
require validation. No claim of PCI DSS compliance is made.
