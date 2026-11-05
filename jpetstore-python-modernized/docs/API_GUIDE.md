# API Guide

Base path: **`/api/v1`**

Operational endpoints: `/health`, `/health/ready`, `/metrics`, `/docs`.

Assessment reference: `../../docs/API_SPECIFICATION.md`.

## Authentication

| Endpoints | Auth |
|-----------|------|
| `/api/v1/catalog/**` (except below) | None (public read) |
| `/api/v1/cart/**` | Bearer JWT required |
| `/api/v1/orders/**` | Bearer JWT + `Idempotency-Key` on checkout |
| `/api/v1/auth/*` | None (rate limited) |
| `/api/v1/account/me*` | Bearer JWT required |

```http
Authorization: Bearer <access_token>
```

---

## Catalog (public)

Optional query params on list endpoints: `limit` (1–100, default 50), `offset` (≥ 0).

### GET `/api/v1/catalog/categories`

**200:** `{ "categories": [...], "total", "limit", "offset" }`

### GET `/api/v1/catalog/categories/{category_id}`

**200:** category object · **404:** unknown category

### GET `/api/v1/catalog/categories/{category_id}/products`

**200:** `{ "category_id", "products", "total", "limit", "offset" }`

### GET `/api/v1/catalog/products/{product_id}`

**200:** product · **404:** not found

### GET `/api/v1/catalog/products/{product_id}/items`

**200:** `{ "product_id", "items": [{ "item_id", "list_price", "attribute1", "in_stock", ... }] }`  
`in_stock`: inventory qty &gt; 0 (read-only).

### GET `/api/v1/catalog/items/{item_id}`

**200:** item + nested `product` + `quantity` · **404:** invalid item

### GET `/api/v1/catalog/products/search?keyword=...`

Primary search (FR-1.4). **400** if keyword missing/blank:

`SEARCH_KEYWORD_REQUIRED` — *Please enter a keyword to search for, then press the search button.*

**200:** `{ "products": [ ... ] }` — duplicate products allowed across tokens (legacy parity).

### GET `/api/v1/catalog/search?q=...`

Alias: accepts `q` or `keyword`.

### GET `/api/v1/catalog/banners`

**200:** `{ "banners": [{ "category_id", "banner_html" }] }`  
`banner_html` is legacy markup; `<script>` blocks and inline event handlers are stripped. Treat as untrusted in clients (JSON only — no server-side HTML rendering).

---

## Account

### POST `/api/v1/auth/register`

**201:** `{ "username" }` — no JWT (FR-3.6). **409:** duplicate username.

### POST `/api/v1/auth/login`

**200:** `{ "access_token", "token_type": "bearer", "expires_in" }`  
**401:** `INVALID_CREDENTIALS`

### GET `/api/v1/account/me` · PUT `/api/v1/account/me`

JWT required. Profile fields per Phase 3; no password in responses.

### GET `/api/v1/account/me/my-list`

**JWT required.** Returns `{ "products": [...] }` for the authenticated user’s **profile favourite category** (FR-3.10). Identity from JWT only — query params cannot select another user’s category.

---

## Cart (JWT required)

All cart routes use identity from JWT `sub` only. Extra fields (e.g. prices) are rejected.

### POST `/api/v1/cart/items`

**Body:** `{ "item_id": "EST-1", "quantity": 1 }` — increment if line exists (FR-2.2).

**400:** unknown `item_id`.

### GET `/api/v1/cart`

**200:**

```json
{
  "cart_id": 1,
  "lines": [
    {
      "item_id": "EST-1",
      "product_id": "FI-SW-01",
      "product_name": "Angelfish",
      "quantity": 2,
      "list_price": "16.50",
      "line_total": "33.00",
      "in_stock": true,
      "item_available": true
    }
  ],
  "sub_total": "33.00"
}
```

Prices are computed server-side on each read. Empty cart: `lines: []`, `sub_total: "0.00"`.

### PUT `/api/v1/cart/items/{item_id}`

**Body:** `{ "quantity": 4 }` — must be ≥ 1 (FR-2.5 style; zero removes via DELETE).

### DELETE `/api/v1/cart/items/{item_id}`

Removes one line (FR-2.4).

### DELETE `/api/v1/cart`

Clears all lines for the authenticated user.

---

## Orders (JWT required)

### POST `/api/v1/orders/checkout`

**Headers:** `Idempotency-Key` (required, max 128 chars)

**Body:** shipping, billing, `courier`, `locale`, synthetic payment (`card_type`, `card_last_four` 4 digits, `expiry_date`). **No CVV.** Extra fields rejected.

**201:** new order — `{ "order_id", "message", "order": { ... } }`  
**200:** idempotent replay (same key + same body)  
**400:** empty cart, invalid item, insufficient inventory  
**409:** idempotency key reused with different body  
**503:** transaction failure

Prices/totals computed server-side from catalog + cart quantities.

### GET `/api/v1/orders`

**200:** `{ "orders": [ { "order_id", "order_date", "total_price", "status" } ] }`

### GET `/api/v1/orders/{order_id}`

**200:** full detail (masked `card_display`, line items)  
**403:** not owner — *You may only view your own orders.*

---

## Environment

| Variable | Purpose |
|----------|---------|
| `JWT_SECRET` | HS256 signing key (min 32 chars) |
| `JWT_*` | See `.env.example` |
| `RATE_LIMIT_*` | Login/register limits |
| `CATALOG_DEFAULT_LIMIT` | Default `50` |
| `CATALOG_MAX_LIMIT` | Default `100` |
| `CATALOG_SEARCH_MAX_LENGTH` | Default `200` |
