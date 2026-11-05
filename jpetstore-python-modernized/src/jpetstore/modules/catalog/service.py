"""Catalog business logic."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from jpetstore.config import Settings
from jpetstore.core.exceptions import AppError
from jpetstore.models import Item, Product
from jpetstore.modules.catalog.repository import CatalogRepository
from jpetstore.modules.catalog.safety import sanitize_banner_html
from jpetstore.modules.catalog.schemas import (
    BannerEntry,
    BannerListResponse,
    CategoryListResponse,
    CategoryProductsResponse,
    CategorySummary,
    ItemDetailResponse,
    ItemSummary,
    ProductItemsResponse,
    ProductListResponse,
    ProductNested,
    ProductSummary,
    SearchProductsResponse,
)


class CatalogService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self._repo = CatalogRepository(session)
        self._settings = settings

    def _clamp_pagination(self, limit: int | None, offset: int | None) -> tuple[int, int]:
        max_limit = self._settings.catalog_max_limit
        default_limit = self._settings.catalog_default_limit
        resolved_limit = default_limit if limit is None else limit
        resolved_offset = 0 if offset is None else offset
        if resolved_limit < 1 or resolved_limit > max_limit:
            raise AppError(
                code="INVALID_PAGINATION",
                message=f"limit must be between 1 and {max_limit}.",
                status_code=400,
            )
        if resolved_offset < 0:
            raise AppError(
                code="INVALID_PAGINATION",
                message="offset must be zero or greater.",
                status_code=400,
            )
        return resolved_limit, resolved_offset

    @staticmethod
    def _product_summary(product: Product) -> ProductSummary:
        return ProductSummary(
            product_id=product.productid,
            category_id=product.category,
            name=product.name,
            description=product.descn,
        )

    @staticmethod
    def _item_summary(item: Item, qty: int | None) -> ItemSummary:
        in_stock = (qty or 0) > 0
        return ItemSummary(
            item_id=item.itemid,
            list_price=item.listprice,
            unit_cost=item.unitcost,
            supplier_id=item.supplier,
            status=item.status,
            attribute1=item.attr1,
            attribute2=item.attr2,
            attribute3=item.attr3,
            attribute4=item.attr4,
            attribute5=item.attr5,
            in_stock=in_stock,
        )

    def list_categories(self, *, limit: int | None, offset: int | None) -> CategoryListResponse:
        lim, off = self._clamp_pagination(limit, offset)
        rows, total = self._repo.list_categories(limit=lim, offset=off)
        categories = [
            CategorySummary(
                category_id=row.catid,
                name=row.name,
                description=row.descn,
            )
            for row in rows
        ]
        return CategoryListResponse(
            categories=categories,
            total=total,
            limit=lim,
            offset=off,
        )

    def get_category(self, category_id: str) -> CategorySummary:
        row = self._repo.get_category(category_id)
        if row is None:
            raise AppError(
                code="CATEGORY_NOT_FOUND",
                message="Category not found.",
                status_code=404,
            )
        return CategorySummary(
            category_id=row.catid,
            name=row.name,
            description=row.descn,
        )

    def list_category_products(
        self,
        category_id: str,
        *,
        limit: int | None,
        offset: int | None,
    ) -> CategoryProductsResponse:
        if self._repo.get_category(category_id) is None:
            raise AppError(
                code="CATEGORY_NOT_FOUND",
                message="Category not found.",
                status_code=404,
            )
        lim, off = self._clamp_pagination(limit, offset)
        rows, total = self._repo.list_products_by_category(
            category_id,
            limit=lim,
            offset=off,
        )
        return CategoryProductsResponse(
            category_id=category_id,
            products=[self._product_summary(p) for p in rows],
            total=total,
            limit=lim,
            offset=off,
        )

    def get_product(self, product_id: str) -> ProductSummary:
        product = self._repo.get_product(product_id)
        if product is None:
            raise AppError(
                code="PRODUCT_NOT_FOUND",
                message="Product not found.",
                status_code=404,
            )
        return self._product_summary(product)

    def list_product_items(self, product_id: str) -> ProductItemsResponse:
        if self._repo.get_product(product_id) is None:
            raise AppError(
                code="PRODUCT_NOT_FOUND",
                message="Product not found.",
                status_code=404,
            )
        items = self._repo.list_items_for_product(product_id)
        qty_map = self._repo.inventory_quantities([item.itemid for item in items])
        return ProductItemsResponse(
            product_id=product_id,
            items=[self._item_summary(item, qty_map.get(item.itemid)) for item in items],
        )

    def get_item(self, item_id: str) -> ItemDetailResponse:
        item = self._repo.get_item(item_id)
        if item is None:
            raise AppError(
                code="ITEM_NOT_FOUND",
                message="Item not found.",
                status_code=404,
            )
        qty_map = self._repo.inventory_quantities([item.itemid])
        qty = qty_map.get(item.itemid, 0)
        product = item.product
        nested = None
        if product is not None:
            nested = ProductNested(
                product_id=product.productid,
                category_id=product.category,
                name=product.name,
                description=product.descn,
            )
        return ItemDetailResponse(
            item_id=item.itemid,
            list_price=item.listprice,
            unit_cost=item.unitcost,
            supplier_id=item.supplier,
            status=item.status,
            attribute1=item.attr1,
            attribute2=item.attr2,
            attribute3=item.attr3,
            attribute4=item.attr4,
            attribute5=item.attr5,
            in_stock=qty > 0,
            quantity=qty,
            product=nested,
        )

    def search_products(self, keyword: str | None) -> SearchProductsResponse:
        if keyword is None or not keyword.strip():
            raise AppError(
                code="SEARCH_KEYWORD_REQUIRED",
                message="Please enter a keyword to search for, then press the search button.",
                status_code=400,
            )
        if len(keyword) > self._settings.catalog_search_max_length:
            raise AppError(
                code="SEARCH_KEYWORD_TOO_LONG",
                message="Search keyword is too long.",
                status_code=400,
            )
        tokens = keyword.lower().split()
        products = self._repo.search_products_by_name_tokens(tokens)
        return SearchProductsResponse(products=[self._product_summary(p) for p in products])

    def list_banners(self) -> BannerListResponse:
        rows = self._repo.list_banners()
        return BannerListResponse(
            banners=[
                BannerEntry(
                    category_id=row.favcategory,
                    banner_html=sanitize_banner_html(row.bannername),
                )
                for row in rows
            ]
        )

    def my_list_products(self, favourite_category_id: str | None) -> ProductListResponse:
        if not favourite_category_id:
            return ProductListResponse(products=[], total=0, limit=0, offset=0)
        products = self._repo.list_products_by_category_unpaged(favourite_category_id)
        summaries = [self._product_summary(p) for p in products]
        return ProductListResponse(
            products=summaries,
            total=len(summaries),
            limit=len(summaries),
            offset=0,
        )
