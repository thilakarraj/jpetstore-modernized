# JPetStore 6 — Functional Requirements (As-Is)

Requirements below are **extracted from implemented behavior** in `jpetstore-6/`. Wording describes what the system does today, not desired future improvements.

**Legend:** `[V]` = verified in source; `[A]` = assumption (e.g. UI label not re-read in JSP).

---

## FR-1 Catalog browsing

| ID | Requirement | Evidence |
|----|-------------|----------|
| FR-1.1 | The system shall display a main catalog page at `/catalog`. | `[V]` `CatalogController.viewMain` |
| FR-1.2 | The system shall list products for a selected category ID. | `[V]` `viewCategory` + `CatalogService.getProductListByCategory` |
| FR-1.3 | The system shall display product details and associated items (SKUs). | `[V]` `viewProduct`, `viewItem` |
| FR-1.4 | The system shall search products by keyword against product name (case-insensitive SQL `LIKE`). | `[V]` `ProductMapper.searchProductList` |
| FR-1.5 | The system shall reject empty search with an error message. | `[V]` `CatalogController.searchProducts` L128–130 |

---

## FR-2 Shopping cart

| ID | Requirement | Evidence |
|----|-------------|----------|
| FR-2.1 | The system shall maintain a per-session shopping cart. | `[V]` Session attribute `cart` |
| FR-2.2 | The system shall add an item to the cart by item ID; adding the same item again increments quantity. | `[V]` `CartController.addItemToCart` |
| FR-2.3 | When adding a **new** line, the system shall record whether inventory quantity &gt; 0 at add time (`inStock` flag on cart line). | `[V]` `catalogService.isItemInStock` + `Cart.addItem` |
| FR-2.4 | The system shall remove cart lines by item ID. | `[V]` `removeItemFromCart` |
| FR-2.5 | The system shall update line quantities from a form POST; quantity &lt; 1 removes the line. | `[V]` `updateCartQuantities` |
| FR-2.6 | The system shall compute cart subtotal as sum of (item list price × quantity). | `[V]` `Cart.getSubTotal` |
| FR-2.7 | The system shall provide a checkout page view for the current cart. | `[V]` `CartController.checkOut` |

---

## FR-3 Account and profile

| ID | Requirement | Evidence |
|----|-------------|----------|
| FR-3.1 | The system shall authenticate users with username and password against `signon` + joined account data. | `[V]` `AccountService.getAccount(u,p)`, `AccountMapper.getAccountByUsernameAndPassword` |
| FR-3.2 | Failed sign-on shall display “Invalid username or password. Signon failed.” | `[V]` `AccountController.signon` L93 |
| FR-3.3 | Successful sign-on shall store account in session without password and redirect to catalog. | `[V]` L96–99 |
| FR-3.4 | The system shall allow session sign-off (invalidate session). | `[V]` `signoff` |
| FR-3.5 | The system shall register a new account by inserting rows in `account`, `profile`, and `signon`. | `[V]` `AccountService.insertAccount` |
| FR-3.6 | Registration shall redirect to catalog without establishing an authenticated session. | `[V]` `newAccount` return value |
| FR-3.7 | Authenticated users shall edit account and profile fields; optional password change when password field non-empty. | `[V]` `AccountService.updateAccount` |
| FR-3.8 | The system shall expose language preference options `english` and `japanese` on account forms. | `[V]` `AccountController.LANGUAGE_LIST` |
| FR-3.9 | The system shall expose favourite pet categories FISH, DOGS, REPTILES, CATS, BIRDS on account forms. | `[V]` `AccountController.CATEGORY_LIST` |
| FR-3.10 | After sign-on or profile update, the system shall load “My List” products for the user’s favourite category into session. | `[V]` `AccountSession.myList` population |

---

## FR-4 Orders

| ID | Requirement | Evidence |
|----|-------------|----------|
| FR-4.1 | Only authenticated users may start checkout (`/order/new`). | `[V]` `OrderController.newOrderForm` |
| FR-4.2 | Checkout requires a non-null session cart; otherwise error message. | `[V]` L117–118 |
| FR-4.3 | New order shall be prefilled from account addresses and cart contents. | `[V]` `Order.initOrder` |
| FR-4.4 | Checkout shall collect billing/payment and optional separate shipping address (multi-page flow via POST `/order/new`). | `[V]` `OrderController.newOrder` |
| FR-4.5 | Order confirmation shall persist order, initial order status, line items, and decrement inventory. | `[V]` `OrderService.insertOrder` |
| FR-4.6 | After successful submit, cart shall be emptied. | `[V]` `session.setAttribute("cart", new Cart())` |
| FR-4.7 | Authenticated users shall list their orders by username. | `[V]` `listOrders` + `getOrdersByUsername` |
| FR-4.8 | Users shall view order detail only for orders owned by their username. | `[V]` `viewOrder` L229–234 |
| FR-4.9 | Order IDs shall be generated from database sequence name `ordernum`. | `[V]` `getNextId("ordernum")`, seed data |

---

## FR-5 Presentation and navigation

| ID | Requirement | Evidence |
|----|-------------|----------|
| FR-5.1 | Global header shall link to cart, sign-in/out, account edit, help, and category quick links. | `[V]` `IncludeTop.jsp` |
| FR-5.2 | Product search shall be available from the header form. | `[V]` `IncludeTop.jsp` L67–70 |

---

## FR-6 Data integrity (functional, as implemented)

| ID | Requirement | Evidence |
|----|-------------|----------|
| FR-6.1 | Line item unit price stored at order time from item list price. | `[V]` `LineItem(CartItem)` |
| FR-6.2 | Order header `totalprice` set from cart subtotal at order init (not recalculated at insert in service). | `[V]` `Order.initOrder` |
| FR-6.3 | Initial order status code stored as `P` on the order object and inserted into `orderstatus`. | `[V]` `Order.initOrder`, `insertOrderStatus` |

---

## Explicit non-requirements (not present in code)

- Role-based admin functions.
- Real-time payment authorization.
- Shipment tracking updates.
- Password hashing.
- Email verification on registration.
- Wishlist beyond “My List” category product listing.

These are **observed absences**; do not treat as future scope unless product owners add them.
