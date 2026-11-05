"""Catalog API response schemas."""

from decimal import Decimal

from pydantic import BaseModel, Field


class CategorySummary(BaseModel):
    category_id: str
    name: str | None = None
    description: str | None = None


class CategoryListResponse(BaseModel):
    categories: list[CategorySummary]
    total: int
    limit: int
    offset: int


class ProductSummary(BaseModel):
    product_id: str
    category_id: str
    name: str | None = None
    description: str | None = None


class CategoryProductsResponse(BaseModel):
    category_id: str
    products: list[ProductSummary]
    total: int
    limit: int
    offset: int


class ProductListResponse(BaseModel):
    products: list[ProductSummary]
    total: int
    limit: int
    offset: int


class ItemSummary(BaseModel):
    item_id: str
    list_price: Decimal | None = None
    unit_cost: Decimal | None = None
    supplier_id: int | None = None
    status: str | None = None
    attribute1: str | None = None
    attribute2: str | None = None
    attribute3: str | None = None
    attribute4: str | None = None
    attribute5: str | None = None
    in_stock: bool = False


class ProductItemsResponse(BaseModel):
    product_id: str
    items: list[ItemSummary]


class ProductNested(BaseModel):
    product_id: str
    category_id: str
    name: str | None = None
    description: str | None = None


class ItemDetailResponse(BaseModel):
    item_id: str
    list_price: Decimal | None = None
    unit_cost: Decimal | None = None
    supplier_id: int | None = None
    status: str | None = None
    attribute1: str | None = None
    attribute2: str | None = None
    attribute3: str | None = None
    attribute4: str | None = None
    attribute5: str | None = None
    in_stock: bool = False
    quantity: int = 0
    product: ProductNested | None = None


class SearchProductsResponse(BaseModel):
    products: list[ProductSummary]


class BannerEntry(BaseModel):
    category_id: str
    banner_html: str | None = Field(
        default=None,
        description="Legacy HTML; treat as untrusted. Script tags are stripped server-side.",
    )


class BannerListResponse(BaseModel):
    banners: list[BannerEntry]
