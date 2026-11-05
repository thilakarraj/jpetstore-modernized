# JPetStore 6 — Data Model

**Canonical schema:** `jpetstore-6/src/main/resources/database/jpetstore-hsqldb-schema.sql`  
**Seed data:** `jpetstore-6/src/main/resources/database/jpetstore-hsqldb-dataload.sql`  
**Domain ↔ persistence:** MyBatis mappers in `src/main/resources/org/mybatis/jpetstore/mapper/`.

---

## 1. Entity-relationship overview

```mermaid
erDiagram
  CATEGORY ||--o{ PRODUCT : contains
  PRODUCT ||--o{ ITEM : has
  SUPPLIER ||--o{ ITEM : supplies
  ITEM ||--|| INVENTORY : qty
  ACCOUNT ||--|| PROFILE : extends
  ACCOUNT ||--|| SIGNON : credentials
  PROFILE }o--|| BANNERDATA : favcategory
  ORDERS ||--o{ LINEITEM : contains
  ORDERS ||--o{ ORDERSTATUS : status_rows
  ITEM ||--o{ LINEITEM : ordered_as
  SEQUENCE : standalone
```

**Verified:** FK constraints exist for `product.category → category.catid`, `item.productid → product.productid`, `item.supplier → supplier.suppid` (schema L125–149).

**Verified gaps:** No FK from `orders.userid` to `account.userid`, `lineitem.itemid` to `item.itemid`, or `inventory.itemid` to `item.itemid`.

---

## 2. Tables

### Catalog

| Table | PK | Notable columns | Java domain |
|-------|-----|-----------------|-------------|
| `category` | `catid` | `name`, `descn` | `Category` |
| `product` | `productid` | `category` (FK), `name`, `descn` | `Product` |
| `item` | `itemid` | `productid` (FK), `listprice`, `unitcost`, `supplier` (FK), `status`, `attr1`–`attr5` | `Item` |
| `inventory` | `itemid` | `qty` | `Item.quantity` when loaded via joins |
| `supplier` | `suppid` | address fields | *No Java class* |

**Indexes (verified):** `productCat`, `productName` on `product`; `itemProd` on `item` (schema L130–152).

### Account / identity

| Table | PK | Notes |
|-------|-----|--------|
| `account` | `userid` | Contact and billing address fields |
| `profile` | `userid` | `langpref`, `favcategory`, `mylistopt`, `banneropt` |
| `signon` | `username` | `password` (plain text in seed data) |
| `bannerdata` | `favcategory` | `bannername` (HTML snippet) |

**Java aggregate:** `Account` maps columns from `account`, `profile`, `signon`, and `bannerdata` in `AccountMapper.xml` (`getAccountByUsername`, `getAccountByUsernameAndPassword`).

### Orders

| Table | PK | Notes |
|-------|-----|--------|
| `orders` | `orderid` | Shipping/billing addresses, payment fields, `totalprice`, `courier`, `locale`, `userid` |
| `lineitem` | `(orderid, linenum)` | `itemid`, `quantity`, `unitprice` |
| `orderstatus` | `(orderid, linenum)` | `timestamp`, `status` — initial row inserted on order create |
| `sequence` | `name` | `nextid` — used for `ordernum` |

**Java:** `Order`, `LineItem`; `Sequence` for ID generation only.

---

## 3. Domain object relationships (in-memory)

| Object | Relationships | Source |
|--------|---------------|--------|
| `Product` | `categoryId` → category | `Product.java`; loaded without nested `Category` object |
| `Item` | nested `Product`; optional `quantity` from inventory | `Item.java`; `ItemMapper.getItem` |
| `Cart` / `CartItem` | `CartItem` → `Item`; not persisted | Session-only |
| `Order` | `List<LineItem>`; each `LineItem` may hold nested `Item` after `OrderService.getOrder` | `Order.java`, `OrderService.java` |
| `Account` | favourite category drives “My List” products in session | `AccountController.signon` |

---

## 4. Column ↔ property mapping (MyBatis)

Representative mappings (full SQL in mapper XML):

| Mapper | Operation | Mapping notes |
|--------|-----------|---------------|
| `CategoryMapper` | `getCategory`, `getCategoryList` | `CATID` → `categoryId`, `DESCN` → `description` |
| `ProductMapper` | CRUD reads | `DESCN` → `description`, `CATEGORY` → `categoryId` |
| `ProductMapper` | `searchProductList` | `lower(name) like #{value}` |
| `ItemMapper` | `getItem`, `getItemListByProduct` | Nested `product.*`; `getItem` joins `inventory` for `QTY` → `quantity` |
| `ItemMapper` | `updateInventoryQuantity` | `QTY = QTY - #{increment}` |
| `AccountMapper` | reads/writes | Split across `account`, `profile`, `signon`; boolean options as 0/1 |
| `OrderMapper` | reads | Join `orders` + `orderstatus` for `STATUS` |
| `OrderMapper` | `insertOrderStatus` | Inserts `(orderid, linenum, timestamp, status)` — **linenum bound to `orderId`** (see L104–106 `OrderMapper.xml`) |
| `LineItemMapper` | insert/select | Standard line fields |
| `SequenceMapper` | get/update | `nextid` ↔ `Sequence.nextId` |

---

## 5. Sample / seed data (verified excerpts)

From `jpetstore-hsqldb-dataload.sql`:

| Data set | Examples |
|----------|----------|
| Sequence | `ordernum` starts at **1000** (L17) |
| Users | `j2ee`/`j2ee`, `ACID`/`ACID` signon (L19–20); matching `account` + `profile` rows |
| Categories | `FISH`, `DOGS`, `REPTILES`, `CATS`, `BIRDS` (L34–38) |
| Products | e.g. `FI-SW-01` Angelfish, `FI-FW-02` Goldfish (L40–55) |
| Items | `EST-1` … `EST-28` with `listprice`, `attr1` variant labels (L60–87) |
| Inventory | Each `EST-*` item **qty 10000** (L89–116) |
| Suppliers | IDs 1 and 2 (L57–58) |
| Banner HTML | Per favourite category (L28–32) |

**Orders in seed file:** No preloaded rows in `orders` / `lineitem` / `orderstatus` in `dataload.sql` (verified: file ends after inventory inserts).

---

## 6. Persistence not exposed to application layer

| Table | Used in SQL | Application API |
|-------|-------------|-----------------|
| `supplier` | FK on `item`; seed data | No read/update APIs |
| `orderstatus` | Insert on order; join on read | No status workflow after create |
| `bannerdata` | Join in account queries | Display via `Account.bannerName` only |

---

## 7. Behavioral data rules (from code + SQL)

| Rule | Verified? | Evidence |
|------|-----------|----------|
| Order ID from sequence `ordernum` | Yes | `OrderService.insertOrder` → `getNextId("ordernum")`; seed `sequence` row |
| Line numbers assigned 1..n in cart order | Yes | `Order.addLineItem(CartItem)` uses `lineItems.size() + 1` |
| Unit price on order line = item list price at checkout time | Yes | `LineItem` constructor from `CartItem` |
| Order total = cart subtotal at init | Yes | `Order.initOrder` sets `totalPrice = cart.getSubTotal()` |
| Inventory decremented on order insert | Yes | `ItemMapper.updateInventoryQuantity` before order insert |
| Stock check when adding new cart line | Yes | `CatalogService.isItemInStock` in `CartController.addItemToCart` |
| Stock check at order submit | **No** | Not found in `OrderService` or `OrderController` |
