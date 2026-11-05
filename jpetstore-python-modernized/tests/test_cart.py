"""Phase 5 persistent cart tests."""

from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from jpetstore.core.exceptions import AppError
from jpetstore.models import Cart, CartItem, Item
from jpetstore.modules.cart.repository import CartRepository
from jpetstore.seed import legacy_data
from seed_helpers import seed_catalog

REGISTER = {
    "username": "cartuser",
    "password": "SecretPass1",
    "email": "cart@example.com",
    "first_name": "C",
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


def _auth_token(client: TestClient, username: str = "cartuser") -> str:
    body = {**REGISTER, "username": username}
    client.post("/api/v1/auth/register", json=body)
    login = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "SecretPass1"},
    )
    return login.json()["access_token"]


@pytest.fixture
def cart_client(api_client: TestClient, db_engine) -> TestClient:
    with Session(db_engine) as session:
        seed_catalog(session)
    return api_client


def test_add_item_creates_cart(cart_client: TestClient) -> None:
    token = _auth_token(cart_client)
    response = cart_client.post(
        "/api/v1/cart/items",
        json={"item_id": "EST-1", "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["cart_id"] > 0
    assert len(body["lines"]) == 1
    assert body["lines"][0]["list_price"] == "16.50"
    assert body["sub_total"] == "16.50"
    assert "password" not in response.text


def test_add_existing_item_increments(cart_client: TestClient) -> None:
    token = _auth_token(cart_client, "incuser")
    headers = {"Authorization": f"Bearer {token}"}
    cart_client.post("/api/v1/cart/items", json={"item_id": "EST-1", "quantity": 2}, headers=headers)
    cart_client.post("/api/v1/cart/items", json={"item_id": "EST-1", "quantity": 3}, headers=headers)
    response = cart_client.get("/api/v1/cart", headers=headers)
    assert response.json()["lines"][0]["quantity"] == 5


def test_get_empty_cart(cart_client: TestClient) -> None:
    token = _auth_token(cart_client, "emptycart")
    response = cart_client.get(
        "/api/v1/cart",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["lines"] == []
    assert response.json()["sub_total"] == "0.00"


def test_update_quantity(cart_client: TestClient) -> None:
    token = _auth_token(cart_client, "qtyuser")
    headers = {"Authorization": f"Bearer {token}"}
    cart_client.post("/api/v1/cart/items", json={"item_id": "EST-1", "quantity": 1}, headers=headers)
    response = cart_client.put(
        "/api/v1/cart/items/EST-1",
        json={"quantity": 4},
        headers=headers,
    )
    assert response.json()["lines"][0]["quantity"] == 4
    assert response.json()["sub_total"] == "66.00"


def test_reject_zero_quantity_update(cart_client: TestClient) -> None:
    token = _auth_token(cart_client, "zerouser")
    headers = {"Authorization": f"Bearer {token}"}
    cart_client.post("/api/v1/cart/items", json={"item_id": "EST-1", "quantity": 1}, headers=headers)
    response = cart_client.put(
        "/api/v1/cart/items/EST-1",
        json={"quantity": 0},
        headers=headers,
    )
    assert response.status_code == 422


def test_reject_negative_add(cart_client: TestClient) -> None:
    token = _auth_token(cart_client, "neguser")
    response = cart_client.post(
        "/api/v1/cart/items",
        json={"item_id": "EST-1", "quantity": -1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_remove_item(cart_client: TestClient) -> None:
    token = _auth_token(cart_client, "remuser")
    headers = {"Authorization": f"Bearer {token}"}
    cart_client.post("/api/v1/cart/items", json={"item_id": "EST-1", "quantity": 1}, headers=headers)
    response = cart_client.delete("/api/v1/cart/items/EST-1", headers=headers)
    assert response.json()["lines"] == []


def test_clear_cart(cart_client: TestClient) -> None:
    token = _auth_token(cart_client, "clruser")
    headers = {"Authorization": f"Bearer {token}"}
    cart_client.post("/api/v1/cart/items", json={"item_id": "EST-1", "quantity": 1}, headers=headers)
    cart_client.post("/api/v1/cart/items", json={"item_id": "EST-2", "quantity": 1}, headers=headers)
    response = cart_client.delete("/api/v1/cart", headers=headers)
    assert response.json()["lines"] == []
    assert response.json()["sub_total"] == "0.00"


def test_unknown_item_rejected(cart_client: TestClient) -> None:
    token = _auth_token(cart_client, "baditem")
    response = cart_client.post(
        "/api/v1/cart/items",
        json={"item_id": "NO-SUCH", "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400


def test_requires_jwt(cart_client: TestClient) -> None:
    assert cart_client.get("/api/v1/cart").status_code == 401


def test_reject_client_price_fields(cart_client: TestClient) -> None:
    token = _auth_token(cart_client, "priceuser")
    response = cart_client.post(
        "/api/v1/cart/items",
        json={"item_id": "EST-1", "quantity": 1, "list_price": "0.01"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_recalculate_price_from_catalog(cart_client: TestClient, db_engine) -> None:
    token = _auth_token(cart_client, "recalc")
    headers = {"Authorization": f"Bearer {token}"}
    cart_client.post("/api/v1/cart/items", json={"item_id": "EST-1", "quantity": 2}, headers=headers)
    with Session(db_engine) as session:
        item = session.get(Item, "EST-1")
        assert item is not None
        item.listprice = Decimal("20.00")
        session.commit()
    response = cart_client.get("/api/v1/cart", headers=headers)
    assert response.json()["lines"][0]["list_price"] == "20.00"
    assert response.json()["sub_total"] == "40.00"


def test_decimal_line_total(cart_client: TestClient) -> None:
    token = _auth_token(cart_client, "decuser")
    headers = {"Authorization": f"Bearer {token}"}
    cart_client.post("/api/v1/cart/items", json={"item_id": "EST-21", "quantity": 3}, headers=headers)
    response = cart_client.get("/api/v1/cart", headers=headers)
    line = response.json()["lines"][0]
    assert line["list_price"] == "5.29"
    assert line["line_total"] == "15.87"


def test_persistence_across_sessions(cart_client: TestClient, db_engine) -> None:
    token = _auth_token(cart_client, "persist")
    headers = {"Authorization": f"Bearer {token}"}
    cart_client.post("/api/v1/cart/items", json={"item_id": "EST-3", "quantity": 2}, headers=headers)
    with sessionmaker(bind=db_engine, future=True)() as session:
        carts = session.scalars(select(Cart).where(Cart.userid == "persist")).all()
        assert len(carts) == 1
        assert len(carts[0].items) == 1


def test_users_have_separate_carts(cart_client: TestClient) -> None:
    token_a = _auth_token(cart_client, "usera")
    token_b = _auth_token(cart_client, "userb")
    cart_client.post(
        "/api/v1/cart/items",
        json={"item_id": "EST-1", "quantity": 5},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    cart_client.post(
        "/api/v1/cart/items",
        json={"item_id": "EST-1", "quantity": 1},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    cart_a = cart_client.get("/api/v1/cart", headers={"Authorization": f"Bearer {token_a}"})
    cart_b = cart_client.get("/api/v1/cart", headers={"Authorization": f"Bearer {token_b}"})
    assert cart_a.json()["lines"][0]["quantity"] == 5
    assert cart_b.json()["lines"][0]["quantity"] == 1


def test_concurrent_cart_creation(db_engine) -> None:
    with Session(db_engine) as session:
        seed_catalog(session)
        from jpetstore.models import Account

        session.add(
            Account(
                userid="conc",
                email="c@e.com",
                firstname="C",
                lastname="U",
                status="OK",
                addr1="1",
                addr2=None,
                city="C",
                state="S",
                zip="1",
                country="USA",
                phone="1",
            )
        )
        session.commit()
    with sessionmaker(bind=db_engine, future=True)() as s1, sessionmaker(
        bind=db_engine, future=True
    )() as s2:
        repo1 = CartRepository(s1)
        repo2 = CartRepository(s2)
        c1 = repo1.get_or_create_active_cart("conc")
        s1.commit()
        c2 = repo2.get_or_create_active_cart("conc")
        s2.commit()
        assert c1.cart_id == c2.cart_id


def test_transaction_rollback_on_bad_item(db_engine) -> None:
    with Session(db_engine) as session:
        seed_catalog(session)
        from jpetstore.models import Account, Signon
        from jpetstore.security.passwords import hash_password

        session.add(
            Account(
                userid="rb",
                email="r@e.com",
                firstname="R",
                lastname="B",
                status="OK",
                addr1="1",
                addr2=None,
                city="C",
                state="S",
                zip="1",
                country="USA",
                phone="1",
            )
        )
        session.add(Signon(username="rb", password=hash_password("x")))
        session.commit()
    from jpetstore.modules.account.service import AuthUser
    from jpetstore.modules.cart.service import CartService
    from jpetstore.modules.cart.schemas import AddCartItemRequest

    session = sessionmaker(bind=db_engine, future=True)()
    service = CartService(session)
    with pytest.raises(AppError):
        service.add_item(AuthUser(username="rb"), AddCartItemRequest(item_id="MISSING", quantity=1))
    session.rollback()
    session.close()
    with sessionmaker(bind=db_engine, future=True)() as check:
        count = check.scalar(select(func.count()).select_from(Cart).where(Cart.userid == "rb"))
        assert count == 0
