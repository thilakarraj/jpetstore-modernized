# JPetStore 6 — Technical Requirements (Modernization Targets)

This document captures **technical constraints and qualities** observed in the Java application that a Python replacement should either **preserve** (parity) or **consciously address**. It does not prescribe Python frameworks.

---

## TR-1 Runtime and deployment

| ID | Requirement | As-is detail | Modernization note |
|----|-------------|--------------|-------------------|
| TR-1.1 | Deploy as web application with HTML UI | WAR + JSP + static assets | Preserve URL semantics where tests/docs depend on them |
| TR-1.2 | Java 11 bytecode | `pom.xml` | N/A for Python; document equivalent runtime version policy separately |
| TR-1.3 | Default IT server Tomcat 9 | Cargo profile `tomcat9` | E2E tests assume deployed context (see TR-7) |
| TR-1.4 | Embedded database on startup | HSQLDB via Spring `embedded-database` | Python port needs equivalent schema + seed scripts (`jpetstore-hsqldb-schema.sql`, `jpetstore-hsqldb-dataload.sql`) |

---

## TR-2 Application architecture

| ID | Requirement | Evidence |
|----|-------------|----------|
| TR-2.1 | Layered design: web → service → persistence | Controllers, `@Service`, MyBatis mappers |
| TR-2.2 | Spring root context for services/DAO; MVC child context for controllers | `applicationContext.xml`, `spring-mvc.xml`, `web.xml` |
| TR-2.3 | Constructor injection in services | `OrderService`, `CatalogService`, `AccountService` |
| TR-2.4 | No dedicated cart/order web service layer for reads | Cart in session; order merge logic in `OrderController` |

---

## TR-3 Persistence

| ID | Requirement | Evidence |
|----|-------------|----------|
| TR-3.1 | SQL access via mapped statements (not JPA) | MyBatis XML mappers |
| TR-3.2 | Type aliases for all domain classes in `org.mybatis.jpetstore.domain` | `SqlSessionFactoryBean` |
| TR-3.3 | Second-level cache enabled on all mapper namespaces | `<cache />` in each `*Mapper.xml` |
| TR-3.4 | Order ID generation via optimistic read/update of `sequence` row | `SequenceMapper` + `OrderService.getNextId` |
| TR-3.5 | Inventory update: `UPDATE inventory SET qty = qty - :increment` with no lower bound | `ItemMapper.xml` L76–79 |

---

## TR-4 Transactions

| ID | Boundary | Operations | Annotation / manager |
|----|----------|------------|---------------------|
| TR-4.1 | **Order insert** | Sequence bump (via `getNextId`), inventory decrements, order insert, order status insert, line inserts | `@Transactional` on `OrderService.insertOrder` |
| TR-4.2 | **Order read (detail)** | Load order, lines, items, inventory qty per line | `@Transactional` on `OrderService.getOrder` |
| TR-4.3 | **Account create** | insert account, profile, signon | `@Transactional` on `AccountService.insertAccount` |
| TR-4.4 | **Account update** | update account, profile, optional signon | `@Transactional` on `AccountService.updateAccount` |
| TR-4.5 | **Catalog reads** | No transaction annotations | Default auto-commit per call |

**Verified ordering inside TR-4.1** (`OrderService.insertOrder`):

1. `order.setOrderId(getNextId("ordernum"))`
2. For each line: `updateInventoryQuantity`
3. `insertOrder`
4. `insertOrderStatus`
5. For each line: `insertLineItem`

**Rollback expectation (inferred, not runtime-tested here):** Spring should roll back all JDBC work in TR-4.1 if any step throws after transaction start. `[A]` Confirm with integration test in Python port.

**Concurrency gap (verified code):** `getNextId` is not isolated with row locking; concurrent orders may collide on sequence or interleave inventory updates unless DB isolation prevents it.

---

## TR-5 Security

| ID | Topic | As-is behavior | Parity vs improve |
|----|-------|----------------|-------------------|
| TR-5.1 | Authentication | Session attribute `accountBean`; form login | Preserve session semantics or document migration to tokens |
| TR-5.2 | Authorization | Controller checks only | No global filter |
| TR-5.3 | Password storage | Plain text in `signon.password` (seed and mapper) | **Observed**; modernization usually hashes—flag as intentional change if improved |
| TR-5.4 | PCI / secrets | Credit card numbers persisted in `orders.creditcard` | Demo behavior; do not expand scope without approval |
| TR-5.5 | CSRF | No tokens on forms | Many mutating actions use GET (`/cart/addItem`) |
| TR-5.6 | Transport | Not enforced in app | Assume HTTPS at edge in production `[A]` |

---

## TR-6 Reliability and data quality

| ID | Issue | Evidence |
|----|-------|----------|
| TR-6.1 | Inventory can go negative | No `WHERE qty >= increment` on update |
| TR-6.2 | No order-time stock validation | `insertOrder` does not check qty |
| TR-6.3 | Cart `inStock` flag may become stale | Set only when line first added |
| TR-6.4 | `insertOrderStatus` uses `orderId` for both `orderid` and `linenum` columns | `OrderMapper.xml` L104–106 |
| TR-6.5 | Duplicate products in multi-word search | `CatalogService.searchProductList` appends to list without deduplication |
| TR-6.6 | `CatalogController.viewItem` assumes non-null item/product | No null guard if invalid `itemId` |

---

## TR-7 Performance and caching

| ID | Topic | Detail |
|----|-------|--------|
| TR-7.1 | MyBatis L2 cache | Enabled per mapper; stale inventory/catalog reads possible until cache flush/evict |
| TR-7.2 | Embedded HSQLDB | Single-node; not representative of production RDBMS scale |
| TR-7.3 | Session state | Cart and partial order in memory—horizontal scaling requires sticky sessions or external session store `[A]` |

---

## TR-8 Observability

| ID | Topic | Detail |
|----|-------|--------|
| TR-8.1 | Logging | SLF4J simple binding; no structured app logging in controllers/services reviewed |
| TR-8.2 | Metrics/tracing | Not present in source tree |

---

## TR-9 Compatibility and test contract

| ID | Contract | Detail |
|----|----------|--------|
| TR-9.1 | Context path | `ScreenTransitionIT` uses `http://127.0.0.1:8080/jpetstore` |
| TR-9.2 | Sample credentials | User `j2ee` / password `j2ee` in seed data |
| TR-9.3 | Order sequence start | First order ID 1000 from seed + `getNextId` semantics |
| TR-9.4 | Unit/integration test suite | Maven Surefire + Failsafe; mapper tests use shared `MapperTestContext` |

---

## TR-10 Servlet / XML stack

| ID | Component | Version (pom) |
|----|-----------|---------------|
| TR-10.1 | Spring MVC annotation mapping | 5.3.x |
| TR-10.2 | JSP + JSTL | Container + taglibs 1.2.5 |
| TR-10.3 | StAX workaround | `StaxFactoryInitializationListener` for some containers |

Python modernization must replace JSP with templates or SPA while mapping the same workflows (`BUSINESS_WORKFLOWS.md`).
