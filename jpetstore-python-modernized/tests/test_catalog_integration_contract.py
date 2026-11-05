"""Catalog API contract tests for frontend integration."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from seed_helpers import seed_catalog


@pytest.fixture
def catalog_client(api_client: TestClient, db_engine) -> TestClient:
    with Session(db_engine) as session:
        seed_catalog(session)
    return api_client


def test_catalog_empty_database_returns_zero_categories(
    api_client: TestClient, db_engine
) -> None:
    response = api_client.get("/api/v1/catalog/categories")
    assert response.status_code == 200
    body = response.json()
    assert body["categories"] == []
    assert body["total"] == 0


def test_catalog_endpoints_match_frontend_contract(catalog_client: TestClient) -> None:
    categories = catalog_client.get("/api/v1/catalog/categories").json()
    assert categories["total"] >= 1
    category_id = categories["categories"][0]["category_id"]

    cat = catalog_client.get(f"/api/v1/catalog/categories/{category_id}").json()
    assert cat["category_id"] == category_id
    assert "name" in cat

    products = catalog_client.get(
        f"/api/v1/catalog/categories/{category_id}/products"
    ).json()
    assert products["category_id"] == category_id
    assert len(products["products"]) >= 1
    product_id = products["products"][0]["product_id"]
    assert "category_id" in products["products"][0]

    product = catalog_client.get(f"/api/v1/catalog/products/{product_id}").json()
    assert product["product_id"] == product_id

    items = catalog_client.get(f"/api/v1/catalog/products/{product_id}/items").json()
    assert items["product_id"] == product_id
    assert len(items["items"]) >= 1
    item_id = items["items"][0]["item_id"]
    assert "list_price" in items["items"][0]
    assert "in_stock" in items["items"][0]

    item = catalog_client.get(f"/api/v1/catalog/items/{item_id}").json()
    assert item["item_id"] == item_id
    assert item.get("product") is not None

    search = catalog_client.get(
        "/api/v1/catalog/products/search", params={"keyword": "fish"}
    ).json()
    assert isinstance(search["products"], list)
