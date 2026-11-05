"""Catalog data access."""

from __future__ import annotations

import time
from collections.abc import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from jpetstore.metrics.prometheus import DATABASE_QUERY_DURATION_SECONDS
from jpetstore.models import BannerData, Category, Inventory, Item, Product


class CatalogRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _timed(self, operation: str, fn):
        start = time.perf_counter()
        try:
            return fn()
        finally:
            elapsed = time.perf_counter() - start
            DATABASE_QUERY_DURATION_SECONDS.labels(operation=operation, outcome="success").observe(
                elapsed
            )

    def list_categories(self, *, limit: int, offset: int) -> tuple[list[Category], int]:
        def run():
            total = self._session.scalar(select(func.count()).select_from(Category)) or 0
            rows = self._session.scalars(
                select(Category).order_by(Category.catid).limit(limit).offset(offset)
            ).all()
            return list(rows), int(total)

        return self._timed("catalog.list_categories", run)

    def get_category(self, category_id: str) -> Category | None:
        return self._timed(
            "catalog.get_category",
            lambda: self._session.get(Category, category_id),
        )

    def list_products_by_category(
        self,
        category_id: str,
        *,
        limit: int,
        offset: int,
    ) -> tuple[list[Product], int]:
        def run():
            total = self._session.scalar(
                select(func.count()).select_from(Product).where(Product.category == category_id)
            ) or 0
            rows = self._session.scalars(
                select(Product)
                .where(Product.category == category_id)
                .order_by(Product.productid)
                .limit(limit)
                .offset(offset)
            ).all()
            return list(rows), int(total)

        return self._timed("catalog.list_products_by_category", run)

    def get_product(self, product_id: str) -> Product | None:
        return self._timed(
            "catalog.get_product",
            lambda: self._session.get(Product, product_id),
        )

    def list_items_for_product(self, product_id: str) -> list[Item]:
        def run():
            return list(
                self._session.scalars(
                    select(Item).where(Item.productid == product_id).order_by(Item.itemid)
                ).all()
            )

        return self._timed("catalog.list_items_for_product", run)

    def get_item(self, item_id: str) -> Item | None:
        def run():
            return self._session.scalar(
                select(Item)
                .where(Item.itemid == item_id)
                .options(joinedload(Item.product))
            )

        return self._timed("catalog.get_item", run)

    def inventory_quantities(self, item_ids: Sequence[str]) -> dict[str, int]:
        if not item_ids:
            return {}

        def run():
            rows = self._session.scalars(
                select(Inventory).where(Inventory.itemid.in_(item_ids))
            ).all()
            return {row.itemid: row.qty for row in rows}

        return self._timed("catalog.inventory_quantities", run)

    def search_products_by_name_tokens(self, tokens: list[str]) -> list[Product]:
        """Legacy parity: one query per token; duplicates preserved in combined list."""

        def run():
            combined: list[Product] = []
            for token in tokens:
                pattern = f"%{token.lower()}%"
                rows = self._session.scalars(
                    select(Product).where(func.lower(Product.name).like(pattern))
                ).all()
                combined.extend(rows)
            return combined

        return self._timed("catalog.search_products", run)

    def list_banners(self) -> list[BannerData]:
        def run():
            return list(
                self._session.scalars(
                    select(BannerData).order_by(BannerData.favcategory)
                ).all()
            )

        return self._timed("catalog.list_banners", run)

    def list_products_by_category_unpaged(self, category_id: str) -> list[Product]:
        def run():
            return list(
                self._session.scalars(
                    select(Product)
                    .where(Product.category == category_id)
                    .order_by(Product.productid)
                ).all()
            )

        return self._timed("catalog.my_list_products", run)
