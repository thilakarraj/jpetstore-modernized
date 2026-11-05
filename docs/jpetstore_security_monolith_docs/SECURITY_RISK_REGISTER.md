# JPetStore Python Security Risk Register --- Modular Monolith

Likelihood (L) and impact (I) use 1--5. Reassess when scope, exposure or
architecture changes.

## 1. Active risks

  ----------------------------------------------------------------------------------------------------------------
  Risk ID  Description                                  L           I       Score Treatment    Rationale/control
  -------- ---------------------------------- ----------- ----------- ----------- ------------ -------------------
  R-001    Synthetic checkout/payment                   1           2           2 Mitigate     No real PAN/CVV;
           reference stored in demo order                                                      synthetic data
                                                                                               only; redact logs

  R-002    Negative inventory allowed at                3           3           9 Accept for   Legacy behavior;
           order submit                                                           parity       strict mode
                                                                                               requires approved
                                                                                               change

  R-003    HS256 symmetric JWT secret                   2           4           8 Mitigate     Strong secret,
                                                                                               short TTL,
                                                                                               rotation; revisit
                                                                                               for production

  R-004    Client logout does not revoke                3           3           9 Accept for   Short TTL; document
           copied access token                                                    assessment   limitation

  R-005    Duplicate products in multi-word             2           1           2 Accept       Legacy parity
           search                                                                              

  R-006    No refresh-token/revocation                  3           3           9 Accept for   Short-lived access
           service                                                                assessment   token; reassess for
                                                                                               production

  R-007    Single application/database is a             2           4           8 Accept       Modular monolith
           common failure boundary                                                             chosen for
                                                                                               simplicity; DB
                                                                                               least privilege

  R-008    MySQL is a single database                   2           4           8 Accept       Assessment scope;
           dependency                                                                          backups and network
                                                                                               isolation required

  R-009    Demo credentials in local/test               4           2           8 Mitigate     Bcrypt hashes;
           fixtures                                                                            disable outside
                                                                                               local/test

  R-010    Legacy                                       1           1           1 Accept for   Preserve only if
           `orderstatus.linenum = order_id`                                       parity       required by
           quirk                                                                               verified legacy
                                                                                               behavior
  ----------------------------------------------------------------------------------------------------------------

## 2. Legacy-only risks

  -----------------------------------------------------------------------
  Risk ID                 Legacy finding          Python treatment
  ----------------------- ----------------------- -----------------------
  L-001                   Plaintext passwords     Bcrypt

  L-002                   Unauthenticated account Authentication required
                          edit                    

  L-003                   Account IDOR            JWT subject is identity

  L-004                   CSRF on order           Bearer-token API; CSRF
                          confirmation            if cookies added

  L-005                   Stored XSS in JSP       Safe data handling and
                                                  UI rendering

  L-006                   Card data               Synthetic reference
                          persisted/displayed     only; no CVV/full PAN
  -----------------------------------------------------------------------

## 3. Risks under mitigation

  ------------------------------------------------------------------------
  Risk ID           Description        Mitigation        Status
  ----------------- ------------------ ----------------- -----------------
  M-001             Dependency CVEs    pip-audit and     Open until CI
                                       pinned            scan
                                       dependencies      

  M-002             Container          Trivy and         Open until image
                    vulnerabilities    non-root image    scan

  M-003             Brute-force login  Rate limiting     Open until tested

  M-004             Duplicate order    Transactional     Open until
                    submission         idempotency       concurrency tests

  M-005             JWT misuse/leakage Strict            Open until tests
                                       validation, short 
                                       TTL, log          
                                       redaction         

  M-006             Cross-user cart    Opaque guest IDs  Open until tests
                    access             and ownership     
                                       checks            

  M-007             CORS/header        Explicit          Open until
                    misconfiguration   deployment        deployed
                                       configuration     verification
  ------------------------------------------------------------------------

## 4. Avoided risks

-   Admin RBAC without requirement.
-   Public internal service endpoints (there are no internal services).
-   Trusting `X-User-Id` from a Gateway.
-   Real payment card storage.
-   Kafka/Redis/Kubernetes for this assessment unless scope changes.
-   JWT localStorage persistence by default.

## 5. Review triggers

Public exposure; cookie authentication; real payment integration;
inventory behavior change; refresh/revocation feature; penetration-test
finding; database/deployment topology change; or use beyond
assessment/demo.

## 6. Sign-off

  Stakeholder                Risks reviewed       Date   Approval
  -------------------------- -------------------- ------ ----------
  Architecture               R-001--R-010                
  Engineering                R-001--R-010, M-\*          
  Security reviewer          All                         
  Product/assessment owner   Parity risks                

Production deployment should not proceed with high-impact risks lacking
an owner and treatment.
