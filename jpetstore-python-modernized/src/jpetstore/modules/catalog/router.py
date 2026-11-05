"""Catalog HTTP routes (public read APIs)."""

from __future__ import annotations

from fastapi import APIRouter, Query

from jpetstore.modules.catalog.dependencies import CatalogServiceDep
from jpetstore.modules.catalog.schemas import (
    BannerListResponse,
    CategoryListResponse,
    CategoryProductsResponse,
    CategorySummary,
    ItemDetailResponse,
    ProductItemsResponse,
    ProductSummary,
    SearchProductsResponse,
)

router = APIRouter(prefix="/api/v1/catalog", tags=["catalog"])


@router.get("/categories", response_model=CategoryListResponse)
def list_categories(
    service: CatalogServiceDep,
    limit: int | None = Query(default=None, ge=1),
    offset: int | None = Query(default=None, ge=0),
) -> CategoryListResponse:
    return service.list_categories(limit=limit, offset=offset)


@router.get("/categories/{category_id}", response_model=CategorySummary)
def get_category(category_id: str, service: CatalogServiceDep) -> CategorySummary:
    return service.get_category(category_id)


@router.get("/categories/{category_id}/products", response_model=CategoryProductsResponse)
def list_category_products(
    category_id: str,
    service: CatalogServiceDep,
    limit: int | None = Query(default=None, ge=1),
    offset: int | None = Query(default=None, ge=0),
) -> CategoryProductsResponse:
    return service.list_category_products(category_id, limit=limit, offset=offset)


@router.get("/products/search", response_model=SearchProductsResponse)
def search_products(
    service: CatalogServiceDep,
    keyword: str | None = Query(default=None, max_length=200),
) -> SearchProductsResponse:
    return service.search_products(keyword)


@router.get("/search", response_model=SearchProductsResponse)
def search_products_alias(
    service: CatalogServiceDep,
    q: str | None = Query(default=None, max_length=200),
    keyword: str | None = Query(default=None, max_length=200),
) -> SearchProductsResponse:
    """Alias for product search (`q` or `keyword`, assessment-compatible)."""
    term = q if q is not None else keyword
    return service.search_products(term)


@router.get("/products/{product_id}", response_model=ProductSummary)
def get_product(product_id: str, service: CatalogServiceDep) -> ProductSummary:
    return service.get_product(product_id)


@router.get("/products/{product_id}/items", response_model=ProductItemsResponse)
def list_product_items(product_id: str, service: CatalogServiceDep) -> ProductItemsResponse:
    return service.list_product_items(product_id)


@router.get("/items/{item_id}", response_model=ItemDetailResponse)
def get_item(item_id: str, service: CatalogServiceDep) -> ItemDetailResponse:
    return service.get_item(item_id)


@router.get("/banners", response_model=BannerListResponse)
def list_banners(service: CatalogServiceDep) -> BannerListResponse:
    return service.list_banners()
