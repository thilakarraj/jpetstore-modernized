# JPetStore Python — API Specification

**Version:** `v1`  
**Base URL (via Gateway):** `http://localhost:8080/api/v1`  
**Formats:** JSON request/response; `Content-Type: application/json` unless noted.

**Global headers:**

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Protected routes | `Bearer {JWT}` |
| `X-Cart-Id` | Guest cart | UUID v4; server creates if absent on first cart call |
| `Idempotency-Key` | `POST /orders` | UUID; duplicate safe |
| `X-Request-Id` | Optional | Echoed in response |

**Error envelope:**

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid username or password. Signon failed."
  },
  "request_id": "..."
}
```

HTTP status follows code table per endpoint.

---

## 1. API Gateway

| Method | Path | Auth | Upstream |
|--------|------|------|----------|
| GET | `/health/live` | None | Gateway |
| GET | `/health/ready` | None | Gateway + backends |

---

## 2. Catalog Service (`/catalog`)

### 2.1 Categories

**GET `/catalog/categories`**

- **FR:** FR-1.2  
- **Response `200`:**

```json
{
  "categories": [
    { "category_id": "FISH", "name": "Fish", "description": "..." }
  ]
}
```

**GET `/catalog/categories/{category_id}`**

- **Response `200`:** single category object  
- **404:** unknown category

**GET `/catalog/categories/{category_id}/products`**

- **Response `200`:**

```json
{
  "category_id": "FISH",
  "products": [
    { "product_id": "FI-SW-01", "category_id": "FISH", "name": "Angelfish", "description": "..." }
  ]
}
```

### 2.2 Products and items

**GET `/catalog/products/{product_id}`**

- **Response `200`:** product object

**GET `/catalog/products/{product_id}/items`**

- **FR:** FR-1.3  
- **Response `200`:**

```json
{
  "product_id": "FI-SW-01",
  "items": [
    {
      "item_id": "EST-1",
      "list_price": "16.50",
      "unit_cost": "10.00",
      "supplier_id": 1,
      "status": "P",
      "attribute1": "Large",
      "in_stock": true
    }
  ]
}
```

`in_stock` from Order Service inventory read (qty > 0).

**GET `/catalog/items/{item_id}`**

- **Response `200`:** item + nested `product` + `quantity` (inventory qty)  
- **404:** invalid item (parity: avoid 500 on bad id)

### 2.3 Search

**GET `/catalog/products/search?keyword={keyword}`**

- **FR:** FR-1.4, FR-1.5  
- **400** if `keyword` missing or empty:

```json
{
  "error": {
    "code": "SEARCH_KEYWORD_REQUIRED",
    "message": "Please enter a keyword to search for, then press the search button."
  }
}
```

- **200:** `{ "products": [ ... ] }` — duplicates allowed across tokens (parity)

---

## 3. Account Service (`/auth`, `/account`)

### 3.1 Register

**POST `/auth/register`**

- **FR:** FR-3.5, FR-3.6, FR-3.8, FR-3.9  
- **Body:**

```json
{
  "username": "newuser",
  "password": "secret",
  "email": "a@b.com",
  "first_name": "A",
  "last_name": "B",
  "address1": "...",
  "address2": null,
  "city": "...",
  "state": "...",
  "zip": "...",
  "country": "...",
  "phone": "...",
  "language_preference": "english",
  "favourite_category_id": "DOGS",
  "list_option": true,
  "banner_option": true
}
```

- **201:** `{ "username": "newuser" }` — **no JWT**  
- **409:** username exists

### 3.2 Login

**POST `/auth/login`**

- **FR:** FR-3.1–FR-3.3  
- **Body:** `{ "username": "j2ee", "password": "j2ee" }` (seed uses legacy password until re-seeded with hashes)

- **200:**

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

- **401:**

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid username or password. Signon failed."
  }
}
```

### 3.3 Profile

**GET `/account/me`**

- **Auth:** JWT  
- **Response `200`:** account + profile fields (no password); includes `banner_name` when resolvable

**PUT `/account/me`**

- **FR:** FR-3.7  
- **Body:** partial account/profile fields; `password` optional — if non-empty, update hash  
- **200:** updated profile

**GET `/account/me/my-list`**

- **FR:** FR-3.10  
- **Response `200`:** `{ "products": [ ... ] }` from favourite category (Catalog)

---

## 4. Order Service (`/cart`, `/checkout`, `/orders`)

### 4.1 Cart

**GET `/cart`**

- **FR:** FR-2.1, FR-2.6  
- **Auth:** JWT and/or `X-Cart-Id`  
- **200:**

```json
{
  "cart_id": "...",
  "lines": [
    {
      "item_id": "EST-20",
      "quantity": 2,
      "in_stock": true,
      "list_price": "5.50",
      "line_total": "11.00"
    }
  ],
  "sub_total": "11.00"
}
```

**POST `/cart/lines`**

- **FR:** FR-2.2, FR-2.3  
- **Body:** `{ "item_id": "EST-20" }`  
- **Behavior:** increment if exists; else fetch item from Catalog, set `in_stock` from qty > 0  
- **400:** invalid item id

**DELETE `/cart/lines/{item_id}`**

- **FR:** FR-2.4

**PUT `/cart/lines`**

- **FR:** FR-2.5  
- **Body:** `{ "lines": [ { "item_id": "EST-20", "quantity": 10 } ] }`  
- Quantities `< 1` remove line; invalid numbers ignored (parity)

### 4.2 Checkout draft

**POST `/checkout/draft`**

- **FR:** FR-4.1–FR-4.3  
- **Auth:** JWT required  
- **Precondition:** non-empty cart  
- **401/403:** not authenticated  
- **400:** empty cart — message parity: *"An order could not be created because a cart could not be found."*

- **200:** prefilled draft (from Account + cart):

```json
{
  "draft_id": "...",
  "username": "j2ee",
  "ship_to_first_name": "...",
  "bill_to_first_name": "...",
  "credit_card": "999 9999 9999 9999",
  "expiry_date": "12/03",
  "card_type": "Visa",
  "courier": "UPS",
  "locale": "CA",
  "status": "P",
  "lines": [ ... ],
  "total_price": "248.50",
  "card_types": ["Visa", "MasterCard", "American Express"]
}
```

**PUT `/checkout/draft/{draft_id}`**

- **FR:** FR-4.4  
- **Body:** partial billing/shipping/payment fields (merge non-null only, parity with `OrderController.newOrder`)  
- **Query:** `shipping_address_required=true` → response indicates next step `shipping` vs `confirm`

**GET `/checkout/draft/{draft_id}`**

- Returns current draft for confirm screen

### 4.3 Place order

**POST `/orders`**

- **FR:** FR-4.5, FR-4.6, FR-4.9  
- **Auth:** JWT  
- **Headers:** `Idempotency-Key` (required)  
- **Body:**

```json
{
  "draft_id": "...",
  "confirmed": true
}
```

- **201:**

```json
{
  "order_id": 1000,
  "message": "Thank you, your order has been submitted.",
  "order": { ... full order detail ... }
}
```

- Clears cart on success  
- **409:** idempotency conflict (different body same key)  
- **503:** transaction failed (inventory/order insert)

**GET `/orders`**

- **FR:** FR-4.7  
- **Auth:** JWT  
- **200:** `{ "orders": [ { "order_id", "order_date", "total_price", "status" } ] }`

**GET `/orders/{order_id}`**

- **FR:** FR-4.8  
- **Auth:** JWT  
- **200:** order + line items + item details  
- **403:** not owner — *"You may only view your own orders."*

---

## 5. Internal APIs (Docker network only)

Not exposed through Gateway.

| Service | Method | Path | Purpose |
|---------|--------|------|---------|
| Catalog | GET | `/internal/items/{item_id}` | Order: validate SKU + list_price |
| Catalog | GET | `/internal/categories/{category_id}` | Account: validate fav category |
| Order | GET | `/internal/inventory/{item_id}` | Catalog: qty for display |
| Account | GET | `/internal/accounts/{username}` | Order: prefill checkout |

Internal responses mirror public models minus auth.

---

## 6. Data types

| Field | Type | Notes |
|-------|------|-------|
| Money | string decimal | `"16.50"` — match `BigDecimal` string habit in JSON |
| `order_date` | ISO 8601 datetime | Legacy display format optional in `formatted_order_date` field |
| IDs | string | `category_id`, `product_id`, `item_id` as legacy |
| `order_id` | integer | From sequence starting 1000 |

---

## 7. OpenAPI

Each service exposes `/openapi.json`; Gateway may publish merged doc at `/api/v1/openapi.json` for clients and AI tools.

---

## 8. FR traceability index

| FR IDs | Primary endpoints |
|--------|-------------------|
| FR-1.* | `/catalog/*` |
| FR-2.* | `/cart/*` |
| FR-3.* | `/auth/*`, `/account/me*` |
| FR-4.* | `/checkout/*`, `/orders*` |
| FR-5.* | Client/UI composition over above APIs |
