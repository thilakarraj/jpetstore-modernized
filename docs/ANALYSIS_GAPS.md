# JPetStore 6 — Analysis Gaps and Open Questions

Items listed here are **limits of this static analysis**, **unverified runtime behavior**, or **known quirks** requiring stakeholder decisions before Python implementation.

---

## 1. Analysis method gaps

| Gap | Impact | Recommended follow-up |
|-----|--------|------------------------|
| Application not executed in this analysis | Transaction isolation, cache invalidation, and exact Tomcat context path unconfirmed at runtime | Run `mvn verify` in `jpetstore-6/` and capture Failsafe/ScreenTransitionIT results |
| JSP field names and validation rules not fully enumerated | Form binding edge cases may be missed | Diff JSP form fields against `@ModelAttribute` / `@RequestParam` lists |
| `jpetstore-hsqldb-data.sql` purpose unclear vs `dataload.sql` | Risk of wrong script in migration | Confirm no build profile references `-data.sql` (grep verified: only schema + dataload in `applicationContext.xml`) |

---

## 2. Test coverage vs functionality

### Covered (verified by test class presence)

| Area | Test classes |
|------|----------------|
| All MyBatis mappers | `*MapperTest.java` (8 mappers) |
| Services | `AccountServiceTest`, `CatalogServiceTest`, `OrderServiceTest` |
| Controllers | `AccountControllerTest`, `CartControllerTest`, `CatalogControllerTest`, `OrderControllerTest`, `RootControllerTest` |
| Domain | `CartTest`, `OrderTest` |
| E2E UI | `ScreenTransitionIT` (10 tests: order, registration, profile, navigation, help, etc.) |
| Servlet listener | `StaxFactoryInitializationListenerTest` |

### Weak or missing coverage (verified gaps)

| Functionality | Gap |
|---------------|-----|
| End-to-end order + DB | `OrderServiceTest.insertOrder` mocks mappers—**no integration test** asserting inventory + order rows after real `insertOrder` |
| Concurrent order / sequence | No tests for parallel `getNextId` |
| Negative inventory | No test expecting failure when qty insufficient |
| Stock at checkout | No test blocking order when cart qty exceeds inventory |
| `CartController.checkOut` | No dedicated test method name in grep summary—may be covered indirectly via view cart tests only |
| `CatalogController.viewItem` invalid ID | No null-safe behavior in controller—likely untested failure mode |
| Authorization bypass | No test for user A viewing user B’s order except `OrderControllerTest` (verify locally) |
| Registration duplicate username | No test referenced in mapper/service for PK violation handling |
| Search deduplication | No test for multi-keyword duplicate products |
| Supplier / banner admin | No tests (no features) |
| GET-based cart mutations | Security/regression not tested |

---

## 3. Behavioral ambiguities

| Topic | What we know | Open question |
|-------|--------------|---------------|
| Order status lifecycle | Only initial `P` row inserted | Should Python implement status updates? **No Java code found.** |
| `orderstatus.linenum` | Insert binds `orderId` to `linenum` | Intentional legacy quirk or bug? Preserve for parity unless DB inspection shows otherwise |
| Shipping flow | Two-step POST with `shippingAddressRequired` | Exact JSP button values not traced in this doc—confirm in `NewOrderForm.jsp` / `ShippingForm.jsp` |
| MyList / banner options | Profile flags `mylistopt`, `banneropt` | UI behavior for disabled options requires JSP review |
| Item `toString` | Assumes `product` non-null | NPE if product not loaded |

---

## 4. Security and compliance gaps (document, do not invent fixes)

| Finding | Source | Decision needed |
|---------|--------|-----------------|
| Plaintext passwords | `signon` table, `AccountMapper` | Parity vs hash at modernization |
| Credit card stored in DB | `orders` columns | Parity vs tokenization |
| CSRF / GET state changes | `CartController` GET add/remove | Accept demo risk vs REST redesign |
| No rate limiting on sign-on | — | Out of scope unless required |

---

## 5. Performance and operations unknowns

| Topic | Notes |
|-------|--------|
| MyBatis cache staleness | After `updateInventoryQuantity`, cached `getItem` / inventory reads may be stale until flush—behavior depends on MyBatis cache config defaults `[A]` |
| Production database | Repo only documents embedded HSQLDB |
| Session replication | Not configured |

---

## 6. Dependencies on unstated environment

| Assumption | Risk |
|------------|------|
| WAR context path `/jpetstore` | Broken links in seed HTML if path differs |
| JDK / module opens for Tomcat 9 | `cargo.jvmargs` in pom for some profiles |
| Chrome available for IT | `ScreenTransitionIT` uses Selenide Chrome headless |

---

## 7. Suggested verification checklist (pre-implementation)

1. Run full Maven test suite and archive Surefire/Failsafe reports.
2. Manually place order for `EST-20` qty 10; confirm inventory 9990 and order id 1000.
3. Attempt order with qty exceeding inventory; document actual DB state (likely negative qty).
4. Sign on as `j2ee`, confirm “My List” shows DOGS products per profile seed.
5. Register new user; confirm redirect without session auth.
6. Confirm `insertOrderStatus` row contents in HSQLDB after one order.

---

## 8. Items explicitly out of analysis scope

- Python framework selection
- UI redesign
- Changes to business rules unless approved after parity baseline
- Modifications to `jpetstore-6/` Java sources (per project constraint)
