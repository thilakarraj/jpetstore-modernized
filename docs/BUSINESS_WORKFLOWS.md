# JPetStore 6 — Customer-Facing Business Workflows

All flows below are derived from controllers in `jpetstore-6/src/main/java/org/mybatis/jpetstore/web/controllers/` and their JSP views unless noted.

---

## 1. Workflow map

```mermaid
flowchart LR
  subgraph browse [Browse and search]
    A[index.html] --> B[/catalog/]
    B --> C[viewCategory]
    B --> D[viewProduct]
    D --> E[viewItem]
    B --> F[searchProducts]
  end
  subgraph cart [Cart]
    E --> G[/cart/addItem]
    G --> H[/cart/]
    H --> I[/cart/update POST]
    H --> J[/cart/checkout]
  end
  subgraph auth [Account]
    K[/account signon]
    L[/account/new]
    M[/account/edit]
    N[/account/signoff]
  end
  subgraph order [Order]
    J --> O[/order/new GET]
    O --> P[/order/new POST]
    P --> Q[Confirm or Shipping]
    Q --> R[Confirm + insertOrder]
    R --> S[ViewOrder]
    T[/order/list]
    U[/order/view]
  end
  K --> O
```

---

## 2. Browse catalog

| Step | HTTP | Handler | Outcome |
|------|------|---------|---------|
| Landing | GET `/` | `RootController.redirectToHome` | Redirect to `/index.html` |
| Store home | GET `/catalog` or `/catalog/` | `CatalogController.viewMain` | View `catalog/Main.jsp` |
| Category | GET `/catalog/viewCategory?categoryId=` | `CatalogController.viewCategory` | Loads products via `CatalogService.getProductListByCategory`, category via `getCategory` → `catalog/Category.jsp` |
| Product | GET `/catalog/viewProduct?productId=` | `CatalogController.viewProduct` | Items via `getItemListByProduct`, product via `getProduct` → `catalog/Product.jsp` |
| Item detail | GET `/catalog/viewItem?itemId=` | `CatalogController.viewItem` | `getItem` (includes product + inventory qty) → `catalog/Item.jsp` |
| Search | GET `/catalog/searchProducts?keyword=` | `CatalogController.searchProducts` | Empty keyword → `common/Error.jsp` with message; else `searchProductList` → `catalog/SearchProducts.jsp` |

**Business rules (verified):**

- Search keywords are lowercased in the controller before service call (`CatalogController` L132).
- `CatalogService.searchProductList` splits input on whitespace and unions SQL `LIKE` results per token (`CatalogService.java` L111–116)—**duplicate products possible** if multiple tokens match.

---

## 3. Shopping cart

| Step | HTTP | Handler | Outcome |
|------|------|---------|---------|
| View cart | GET `/cart` | `CartController.viewCart` | Session `Cart` → `cart/Cart.jsp` |
| Add item | GET `/cart/addItem?workingItemId=` | `CartController.addItemToCart` | Invalid/missing ID → error; duplicate ID increments qty; else loads item, checks stock once, adds → cart view |
| Remove | GET `/cart/removeItem?workingItemId=` | `CartController.removeItemFromCart` | Error if ID invalid or not in cart |
| Update qty | POST `/cart/update` | `CartController.updateCartQuantities` | Reads request params named by `itemId`; qty &lt; 1 removes line; invalid numbers ignored |
| Checkout entry | GET `/cart/checkout` | `CartController.checkOut` | `cart/Checkout.jsp` (does not require sign-in at this step) |

**Session state:** `Cart` stored at `session.cart` (`CartController.getCart`).

**Pricing:** Subtotal = sum of `listPrice × quantity` per line (`Cart.getSubTotal`).

---

## 4. Account registration and sign-on

| Step | HTTP | Handler | Outcome |
|------|------|---------|---------|
| Sign-on form | GET `/account`, `/account/` | `AccountController.signonForm` | `account/SignonForm.jsp` |
| Sign-on | POST `/account/signon` | `AccountController.signon` | Valid credentials → `accountBean` in session, redirect `/catalog`; invalid → message on form |
| Sign-off | GET `/account/signoff` | `AccountController.signoff` | `session.invalidate()`, redirect `/catalog` |
| Register form | GET `/account/new` | `AccountController.newAccountForm` | Languages `english`, `japanese`; categories FISH/DOGS/REPTILES/CATS/BIRDS |
| Register | POST `/account/new` | `AccountController.newAccount` | `AccountService.insertAccount` → redirect `/catalog` (**no auto sign-on**) |
| Edit form | GET `/account/edit` | `AccountController.editAccountForm` | Requires session account |
| Update | POST `/account/edit` | `AccountController.editAccount` | `updateAccount`; refreshes session `accountBean` and “My List” products |

**“My List” (verified):** On sign-on and profile update, `catalogService.getProductListByCategory(account.getFavouriteCategoryId())` populates `AccountSession.myList` for JSP sidebar (`IncludeMyList.jsp`).

---

## 5. Order placement (multi-step)

**Preconditions (verified):**

- GET `/order/new`: Must be authenticated (`accountBean.authenticated`); must have session `cart` (`OrderController.newOrderForm` L104–118).
- Unauthenticated user redirected to `/account` with message (L104–107).

| Step | HTTP | Handler | Outcome |
|------|------|---------|---------|
| Start checkout | GET `/order/new` | `newOrderForm` | Creates session `order` via `Order.initOrder(account, cart)`; defaults payment/shipping from account; `order/NewOrderForm.jsp` |
| Billing / payment | POST `/order/new` | `newOrder` | Merges non-null fields into session order; if `shippingAddressRequired=true` → `order/ShippingForm.jsp`; else → `order/ConfirmOrder.jsp` |
| Shipping | POST `/order/new` (ship fields) | `newOrder` | Same merge logic; typically proceeds to confirm when `shippingAddressRequired` false on second post |
| Confirm | POST `/order/new?confirmed=true` | `newOrder` | **`orderService.insertOrder(sessionOrder)`**; clears cart (`new Cart()`); `order/ViewOrder.jsp` with thank-you message |

**Order initialization defaults (verified in `Order.initOrder`):**

- `status = "P"`, `courier = "UPS"`, `locale = "CA"`, placeholder card `999 9999 9999 9999`, expiry `12/03`, card type `Visa`.
- Ship/bill addresses copied from account.

**Card types offered in UI:** Visa, MasterCard, American Express (`OrderController` CARD_TYPE_LIST).

---

## 6. Order history and detail

| Step | HTTP | Handler | Outcome |
|------|------|---------|---------|
| List | GET `/order/list` | `listOrders` | Requires auth; `getOrdersByUsername` → `order/ListOrders.jsp` |
| Detail | GET `/order/view?orderId=` | `viewOrder` | Requires auth; loads full order via `getOrder`; **denies if username mismatch** → error JSP |

---

## 7. Static / ancillary pages

| Resource | Notes |
|----------|--------|
| `help.html` | Linked from header (`IncludeTop.jsp`) |
| Header search | GET form to `/catalog/searchProducts` |

**E2E coverage:** `ScreenTransitionIT` exercises order path, registration, profile update, category navigation, cart view, help, sidebar/quick links (`jpetstore-6/src/test/java/org/mybatis/jpetstore/ScreenTransitionIT.java`).

---

## 8. Transaction boundary (order submit)

**Verified:** Single service method `OrderService.insertOrder` is `@Transactional` and performs:

1. Allocate `orderId` (`getNextId("ordernum")` — updates `sequence` table).
2. For each line: `itemMapper.updateInventoryQuantity` (decrement).
3. `orderMapper.insertOrder`.
4. `orderMapper.insertOrderStatus`.
5. For each line: `lineItemMapper.insertLineItem`.

See `docs/TECHNICAL_REQUIREMENTS.md` for concurrency and rollback behavior.

---

## 9. Out-of-scope / not implemented (verified by absence)

- Admin catalog or inventory management UI.
- Order status changes after placement (no service updating `orderstatus` beyond initial insert).
- Payment gateway integration (card data stored in DB as entered).
- Email notifications.
