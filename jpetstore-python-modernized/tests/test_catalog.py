"""Catalog module tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from jpetstore.models import Account, BannerData, Profile, Signon
from jpetstore.security.passwords import hash_password
from jpetstore.seed import legacy_data
from seed_helpers import seed_catalog


@pytest.fixture
def catalog_client(api_client: TestClient, db_engine) -> TestClient:
    with Session(db_engine) as session:
        seed_catalog(session)
    return api_client


def test_list_categories(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/catalog/categories")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 5
    assert len(body["categories"]) == 5
    ids = {c["category_id"] for c in body["categories"]}
    assert "FISH" in ids


def test_category_pagination(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/catalog/categories?limit=2&offset=1")
    assert response.status_code == 200
    body = response.json()
    assert body["limit"] == 2
    assert body["offset"] == 1
    assert len(body["categories"]) == 2


def test_get_category(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/catalog/categories/FISH")
    assert response.status_code == 200
    assert response.json()["category_id"] == "FISH"


def test_category_not_found(catalog_client: TestClient) -> None:
    assert catalog_client.get("/api/v1/catalog/categories/NOPE").status_code == 404


def test_list_category_products(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/catalog/categories/FISH/products")
    assert response.status_code == 200
    body = response.json()
    assert body["category_id"] == "FISH"
    assert body["total"] == 4
    product_ids = {p["product_id"] for p in body["products"]}
    assert "FI-SW-01" in product_ids


def test_get_product(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/catalog/products/FI-SW-01")
    assert response.status_code == 200
    assert response.json()["name"] == "Angelfish"


def test_product_not_found(catalog_client: TestClient) -> None:
    assert catalog_client.get("/api/v1/catalog/products/MISSING").status_code == 404


def test_list_product_items(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/catalog/products/FI-SW-01/items")
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 2
    assert items[0]["in_stock"] is True
    assert items[0]["attribute1"] == "Large"


def test_get_item_with_inventory(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/catalog/items/EST-1")
    assert response.status_code == 200
    body = response.json()
    assert body["quantity"] == legacy_data.INVENTORY_QTY
    assert body["product"]["product_id"] == "FI-SW-01"


def test_item_not_found(catalog_client: TestClient) -> None:
    assert catalog_client.get("/api/v1/catalog/items/BAD-ID").status_code == 404


def test_search_requires_keyword(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/catalog/products/search")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "SEARCH_KEYWORD_REQUIRED"


def test_search_empty_keyword(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/catalog/products/search?keyword=%20%20")
    assert response.status_code == 400


def test_search_finds_products(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/catalog/products/search?keyword=fish")
    assert response.status_code == 200
    products = response.json()["products"]
    assert any(p["product_id"] == "FI-SW-01" for p in products)


def test_search_alias_q(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/catalog/search?q=Koi")
    assert response.status_code == 200
    assert any(p["product_id"] == "FI-FW-01" for p in response.json()["products"])


def test_search_duplicate_parity(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/catalog/products/search?keyword=fish%20fish")
    assert response.status_code == 200
    ids = [p["product_id"] for p in response.json()["products"]]
    assert ids.count("FI-SW-01") >= 2


def test_search_sql_injection_safe(catalog_client: TestClient) -> None:
    response = catalog_client.get(
        "/api/v1/catalog/products/search",
        params={"keyword": "zzz999nosql"},
    )
    assert response.status_code == 200
    assert response.json()["products"] == []


def test_banners_strip_scripts(catalog_client: TestClient, db_engine) -> None:
    with Session(db_engine) as session:
        row = session.get(BannerData, "FISH")
        assert row is not None
        row.bannername = '<script>alert(1)</script><image src="/x">'
        session.commit()
    response = catalog_client.get("/api/v1/catalog/banners")
    assert response.status_code == 200
    fish = next(b for b in response.json()["banners"] if b["category_id"] == "FISH")
    assert "<script" not in (fish["banner_html"] or "").lower()


def test_my_list_requires_auth(catalog_client: TestClient) -> None:
    assert catalog_client.get("/api/v1/account/me/my-list").status_code == 401


def test_my_list_from_jwt_favourite_category(catalog_client: TestClient, db_engine) -> None:
    password = "SecretPass1"
    catalog_client.post(
        "/api/v1/auth/register",
        json={
            "username": "dogfan",
            "password": password,
            "email": "dog@example.com",
            "first_name": "D",
            "last_name": "F",
            "address1": "1 Main",
            "address2": None,
            "city": "City",
            "state": "ST",
            "zip": "12345",
            "country": "USA",
            "phone": "555",
            "language_preference": "english",
            "favourite_category_id": "DOGS",
            "list_option": True,
            "banner_option": True,
        },
    )
    login = catalog_client.post(
        "/api/v1/auth/login",
        json={"username": "dogfan", "password": password},
    )
    token = login.json()["access_token"]
    response = catalog_client.get(
        "/api/v1/account/me/my-list",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    products = response.json()["products"]
    assert len(products) == 6
    assert all(p["category_id"] == "DOGS" for p in products)


def test_my_list_uses_jwt_not_query_param(catalog_client: TestClient, db_engine) -> None:
    with Session(db_engine) as session:
        session.add(
            Signon(username="catfan", password=hash_password("SecretPass1"))
        )
        session.add(
            Profile(
                userid="catfan",
                langpref="english",
                favcategory="CATS",
                mylistopt=1,
                banneropt=1,
            )
        )
        session.add(
            Account(
                userid="catfan",
                email="c@example.com",
                firstname="C",
                lastname="F",
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
    login = catalog_client.post(
        "/api/v1/auth/login",
        json={"username": "catfan", "password": "SecretPass1"},
    )
    token = login.json()["access_token"]
    response = catalog_client.get(
        "/api/v1/account/me/my-list?favourite_category_id=DOGS",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert all(p["category_id"] == "CATS" for p in response.json()["products"])
