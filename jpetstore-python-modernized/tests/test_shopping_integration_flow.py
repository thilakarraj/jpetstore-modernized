"""Full-stack shopping workflow against in-memory API (SQLite)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from seed_helpers import seed_catalog
from sqlalchemy.orm import Session

REGISTER = {
    "username": "stackuser1",
    "password": "SecretPass1",
    "email": "stack@example.com",
    "first_name": "Stack",
    "last_name": "User",
    "address1": "1 Main",
    "address2": None,
    "city": "City",
    "state": "ST",
    "zip": "12345",
    "country": "USA",
    "phone": "555-0100",
    "language_preference": "english",
    "favourite_category_id": "FISH",
    "list_option": True,
    "banner_option": True,
}

CHECKOUT = {
    "ship_to_first_name": "Stack",
    "ship_to_last_name": "User",
    "ship_address1": "1 Main",
    "ship_address2": None,
    "ship_city": "City",
    "ship_state": "ST",
    "ship_zip": "12345",
    "ship_country": "USA",
    "bill_to_first_name": "Stack",
    "bill_to_last_name": "User",
    "bill_address1": "1 Main",
    "bill_address2": None,
    "bill_city": "City",
    "bill_state": "ST",
    "bill_zip": "12345",
    "bill_country": "USA",
    "courier": "UPS",
    "locale": "en_US",
    "card_type": "Visa",
    "card_last_four": "9999",
    "expiry_date": "12/30",
}


@pytest.fixture
def shop_client(api_client: TestClient, db_engine) -> TestClient:
    with Session(db_engine) as session:
        seed_catalog(session)
    return api_client


def test_register_login_catalog_cart_checkout_flow(shop_client: TestClient) -> None:
    reg = shop_client.post("/api/v1/auth/register", json=REGISTER)
    assert reg.status_code == 201

    dup = shop_client.post("/api/v1/auth/register", json=REGISTER)
    assert dup.status_code == 409

    bad_login = shop_client.post(
        "/api/v1/auth/login",
        json={"username": REGISTER["username"], "password": "wrong"},
    )
    assert bad_login.status_code == 401

    login = shop_client.post(
        "/api/v1/auth/login",
        json={"username": REGISTER["username"], "password": REGISTER["password"]},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cats = shop_client.get("/api/v1/catalog/categories")
    assert cats.status_code == 200
    assert cats.json()["categories"]

    search = shop_client.get("/api/v1/catalog/products/search", params={"keyword": "Angelfish"})
    assert search.status_code == 200

    items = shop_client.get("/api/v1/catalog/products/FI-SW-01/items")
    assert items.status_code == 200
    item_id = items.json()["items"][0]["item_id"]

    add = shop_client.post(
        "/api/v1/cart/items",
        json={"item_id": item_id, "quantity": 2},
        headers=headers,
    )
    assert add.status_code == 200
    assert float(add.json()["sub_total"]) > 0

    cart = shop_client.get("/api/v1/cart", headers=headers)
    assert cart.status_code == 200
    assert len(cart.json()["lines"]) == 1

    checkout = shop_client.post(
        "/api/v1/orders/checkout",
        json=CHECKOUT,
        headers={**headers, "Idempotency-Key": "e2e-key-1"},
    )
    assert checkout.status_code in (200, 201)
    order_id = checkout.json()["order_id"]

    history = shop_client.get("/api/v1/orders", headers=headers)
    assert history.status_code == 200
    assert any(o["order_id"] == order_id for o in history.json()["orders"])

    detail = shop_client.get(f"/api/v1/orders/{order_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["lines"]

    forbidden = shop_client.get(f"/api/v1/orders/{order_id}")
    assert forbidden.status_code == 401
