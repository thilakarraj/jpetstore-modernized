"""Phase 6 checkout and order tests."""

from __future__ import annotations

import logging
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from jpetstore.core.exceptions import AppError
from jpetstore.logging_setup import get_security_logger
from jpetstore.models import Cart, Inventory, LineItem, Order, OrderStatus, Sequence, Signon
from jpetstore.modules.account.service import AuthUser
from jpetstore.modules.order.schemas import CheckoutRequest
from jpetstore.modules.order.service import OrderService
from jpetstore.security.passwords import hash_password
from seed_helpers import seed_catalog

CHECKOUT_BODY = {
    "ship_to_first_name": "Ship",
    "ship_to_last_name": "User",
    "ship_address1": "1 Ship St",
    "ship_address2": None,
    "ship_city": "City",
    "ship_state": "ST",
    "ship_zip": "12345",
    "ship_country": "USA",
    "bill_to_first_name": "Bill",
    "bill_to_last_name": "User",
    "bill_address1": "1 Bill St",
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

REGISTER = {
    "username": "buyer1",
    "password": "SecretPass1",
    "email": "b@example.com",
    "first_name": "B",
    "last_name": "U",
    "address1": "1 Main",
    "address2": None,
    "city": "City",
    "state": "ST",
    "zip": "12345",
    "country": "USA",
    "phone": "555",
    "language_preference": "english",
    "favourite_category_id": "FISH",
    "list_option": True,
    "banner_option": True,
}


def _token(client: TestClient, username: str = "buyer1") -> str:
    client.post("/api/v1/auth/register", json={**REGISTER, "username": username})
    login = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "SecretPass1"},
    )
    return login.json()["access_token"]


@pytest.fixture
def shop_client(api_client: TestClient, db_engine) -> TestClient:
    with Session(db_engine) as session:
        seed_catalog(session)
    return api_client


def _add_to_cart(client: TestClient, token: str, item_id: str = "EST-1", qty: int = 1) -> None:
    client.post(
        "/api/v1/cart/items",
        json={"item_id": item_id, "quantity": qty},
        headers={"Authorization": f"Bearer {token}"},
    )


def _checkout(
    client: TestClient,
    token: str,
    key: str = "key-1",
    body: dict | None = None,
):
    return client.post(
        "/api/v1/orders/checkout",
        json=body or CHECKOUT_BODY,
        headers={"Authorization": f"Bearer {token}", "Idempotency-Key": key},
    )


def test_checkout_success(shop_client: TestClient, db_engine) -> None:
    token = _token(shop_client, "okbuyer")
    _add_to_cart(shop_client, token, "EST-1", 2)
    response = _checkout(shop_client, token, key="checkout-ok")
    assert response.status_code == 201
    body = response.json()
    assert body["order_id"] == 1000
    assert body["order"]["total_price"] == "33.00"
    assert body["order"]["card_display"] == "****9999"
    assert "9999999999999999" not in response.text
    with Session(db_engine) as session:
        inv = session.get(Inventory, "EST-1")
        assert inv is not None
        assert inv.qty == 10000 - 2
        status = session.scalar(select(OrderStatus).where(OrderStatus.orderid == 1000))
        assert status is not None
        assert status.status == "P"
        cart = session.scalar(select(Cart).where(Cart.userid == "okbuyer"))
        assert cart is not None
        assert cart.status == "checked_out"


def test_empty_cart_rejected(shop_client: TestClient) -> None:
    token = _token(shop_client, "emptybuyer")
    response = _checkout(shop_client, token)
    assert response.status_code == 400


def test_insufficient_inventory(shop_client: TestClient, db_engine) -> None:
    token = _token(shop_client, "lowstock")
    _add_to_cart(shop_client, token, "EST-1", 1)
    with Session(db_engine) as session:
        inv = session.get(Inventory, "EST-1")
        assert inv is not None
        inv.qty = 0
        session.commit()
    response = _checkout(shop_client, token, key="low-inv")
    assert response.status_code == 400
    with Session(db_engine) as session:
        inv = session.get(Inventory, "EST-1")
        assert inv is not None
        assert inv.qty == 0


def test_idempotent_replay(shop_client: TestClient) -> None:
    token = _token(shop_client, "idem")
    _add_to_cart(shop_client, token)
    first = _checkout(shop_client, token, key="same-key")
    assert first.status_code == 201
    second = _checkout(shop_client, token, key="same-key")
    assert second.status_code == 200
    assert second.json()["order_id"] == first.json()["order_id"]


def test_idempotency_conflict(shop_client: TestClient) -> None:
    token = _token(shop_client, "conflict")
    _add_to_cart(shop_client, token)
    _checkout(shop_client, token, key="conf-key")
    alt = {**CHECKOUT_BODY, "courier": "FedEx"}
    response = shop_client.post(
        "/api/v1/orders/checkout",
        json=alt,
        headers={"Authorization": f"Bearer {token}", "Idempotency-Key": "conf-key"},
    )
    assert response.status_code == 409


def test_list_and_get_order(shop_client: TestClient) -> None:
    token = _token(shop_client, "listbuyer")
    _add_to_cart(shop_client, token)
    created = _checkout(shop_client, token, key="list-key")
    order_id = created.json()["order_id"]
    listing = shop_client.get(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert any(o["order_id"] == order_id for o in listing.json()["orders"])
    detail = shop_client.get(
        f"/api/v1/orders/{order_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail.status_code == 200


def test_cannot_view_other_users_order(shop_client: TestClient) -> None:
    token_a = _token(shop_client, "owna")
    token_b = _token(shop_client, "ownb")
    _add_to_cart(shop_client, token_a)
    order_id = _checkout(shop_client, token_a, key="own-key").json()["order_id"]
    response = shop_client.get(
        f"/api/v1/orders/{order_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 403


def test_checkout_requires_jwt(shop_client: TestClient) -> None:
    assert _checkout(shop_client, token="invalid", key="x").status_code == 401


def test_reject_cvv_field(shop_client: TestClient) -> None:
    token = _token(shop_client, "cvv")
    _add_to_cart(shop_client, token)
    body = {**CHECKOUT_BODY, "cvv": "123"}
    assert _checkout(shop_client, token, body=body).status_code == 422


def test_no_full_pan_in_db(shop_client: TestClient, db_engine) -> None:
    token = _token(shop_client, "pan")
    _add_to_cart(shop_client, token)
    _checkout(shop_client, token, key="pan-key")
    with Session(db_engine) as session:
        order = session.get(Order, 1000)
        assert order is not None
        assert order.creditcard == "****9999"


def test_audit_no_payment_secrets(shop_client: TestClient) -> None:
    logger = get_security_logger()
    records: list[logging.LogRecord] = []

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    handler = Capture()
    logger.addHandler(handler)
    token = _token(shop_client, "auditbuy")
    _add_to_cart(shop_client, token)
    _checkout(shop_client, token, key="audit-key")
    logger.removeHandler(handler)
    blob = str([r.__dict__ for r in records])
    assert "9999" not in blob or "card" not in blob.lower()


def test_cart_reactivates_after_checkout(shop_client: TestClient) -> None:
    token = _token(shop_client, "react")
    _add_to_cart(shop_client, token)
    _checkout(shop_client, token, key="react-key")
    add = shop_client.post(
        "/api/v1/cart/items",
        json={"item_id": "EST-2", "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert add.status_code == 200
    assert add.json()["cart_id"] > 0
