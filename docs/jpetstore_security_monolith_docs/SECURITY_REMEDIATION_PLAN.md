# JPetStore Security Remediation Plan --- Modular Monolith

## 1. Architecture baseline

One FastAPI application with Account, Catalog, Cart and Order modules;
one MySQL database/schema; JWT validated inside FastAPI. No Gateway,
microservices, internal HTTP trust headers or service-specific schemas.
React/Vite is a later phase.

## 2. Phase 0 --- Governance

-   Review and approve `SECURITY_ASSESSMENT.md`.
-   Approve `SECURITY_DECISIONS.md`.
-   Review accepted risks in `SECURITY_RISK_REGISTER.md`.
-   Align architecture documents so no Gateway/microservice assumptions
    remain.
-   Require human review for authentication, crypto, payment and order
    transaction code.

Exit: architecture and security decisions agree before implementation.

## 3. Phase 1 --- P0 controls

  -----------------------------------------------------------------------
  Finding / test          Remediation             Module
  ----------------------- ----------------------- -----------------------
  SEC-001 / T-001         Bcrypt password hashing Account

  SEC-002 / T-002         Authenticated profile   Account
                          writes                  

  SEC-003 / T-003         Identity from JWT `sub` Account
                          only                    

  SEC-004 / T-004         Bearer-token API; no    Core/API
                          ambient auth cookie     

  SEC-007 / T-007         Safe profile text       Account/UI
                          handling/rendering      

  SEC-011 / T-011         Synthetic payment only; Order
                          no PAN/CVV              
                          persistence/logging     

  SEC-015 / T-015         Order ownership         Order
                          enforcement             

  SEC-016 / T-016         SQLAlchemy bound        All
                          parameters              

  SEC-021 / T-021         Atomic order            Order
                          transaction             

  SEC-023 / T-023         Atomic idempotency      Order
                          record and order result 

  SEC-036 / T-036         Strict JWT validation   Core/Auth
  -----------------------------------------------------------------------

Exit: all P0 tests pass; no secrets or payment data in logs; transaction
and idempotency behavior verified.

## 4. Phase 2 --- P1 controls

  ------------------------------------------------------------------------------
  Finding / test          Remediation                    Module
  ----------------------- ------------------------------ -----------------------
  SEC-005 / T-005         POST/PUT/DELETE mutations;     Cart
                          guest cart isolation           

  SEC-008 / T-008         Banner URL/text or strict      Catalog
                          sanitization                   

  SEC-009 / T-009         Product description text; safe Catalog/UI
                          UI rendering                   

  SEC-017 / T-017         Pydantic allowlists and reject All
                          unknown fields                 

  SEC-018 / T-018         Password length and            Account
                          confirmation validation        

  SEC-019 / T-019         Preserve negative inventory in Order
                          parity mode; document          

  SEC-020 / T-020         Recompute price/total          Cart/Order
                          server-side                    

  SEC-022 / T-022         Lock sequence row              Order

  SEC-024 / T-024         Rate limit                     Core/API
                          login/register/search/orders   

  SEC-025 / T-025         Security headers               Core/deployment

  SEC-026 / T-026         Explicit CORS allowlist        Core

  SEC-030 / T-030         Structured logs and redaction  Core

  SEC-032 / T-032         pip-audit, Bandit, Semgrep,    CI
                          Gitleaks                       

  SEC-033 / T-033         Trivy scan; non-root runtime   Deployment
  ------------------------------------------------------------------------------

Exit: P0/P1 tests pass; ZAP baseline reviewed with no unresolved High
findings on authentication/order flows.

## 5. Phase 3 --- P2 and operations

-   SEC-006: POST logout if provided; document client-side token
    deletion limitation.
-   SEC-012: disable demo credentials in production-like environment.
-   SEC-013/014: no server session/cookie in bearer-only API; revisit if
    cookies added.
-   SEC-027: reassess SSRF if outbound URL fetching is introduced.
-   SEC-028: fixed or allowlisted redirects only.
-   SEC-029: private MySQL network and least-privilege DB user.
-   SEC-031: backup/restore runbook and restore test.
-   SEC-032: ongoing dependency review.

## 6. Implementation order

1.  Core configuration, database and security utilities.
2.  Account: hashing, registration, login and JWT.
3.  Shared authentication/authorization dependencies.
4.  Catalog and safe content handling.
5.  Cart and cart isolation.
6.  Order: ownership, atomic transaction, idempotency and sequence lock.
7.  CORS, headers, rate limiting, request IDs and log redaction.
8.  Automated security tests.
9.  CI scanning and deployment hardening.
10. Frontend after backend APIs/tests stabilize.

## 7. Out of scope without approval

Admin/RBAC, real payment processor, refresh-token service, distributed
services/API Gateway, Kafka, Redis, Kubernetes, and changing
negative-inventory parity.

## 8. Release gates

Assessment demo: P0 tests pass; relevant exposed P1 tests pass; no real
card data; no committed secrets; DB not public; CORS restricted;
accepted risks disclosed.

Production-like deployment: P0/P1 pass; dynamic scan reviewed;
dependency/container scans reviewed; rate limits/TLS/headers verified;
backup/restore tested; risk register signed.
