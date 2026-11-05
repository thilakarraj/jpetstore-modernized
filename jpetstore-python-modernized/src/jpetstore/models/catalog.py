"""Catalog domain ORM models."""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jpetstore.models.base import Base

if TYPE_CHECKING:
    from jpetstore.models.catalog import Product


class Category(Base):
    __tablename__ = "category"

    catid: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(80))
    descn: Mapped[str | None] = mapped_column(String(255))

    products: Mapped[list["Product"]] = relationship(back_populates="category_rel")


class Product(Base):
    __tablename__ = "product"
    __table_args__ = (
        Index("productCat", "category"),
        Index("productName", "name"),
    )

    productid: Mapped[str] = mapped_column(String(10), primary_key=True)
    category: Mapped[str] = mapped_column(
        String(10), ForeignKey("category.catid"), nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(80))
    descn: Mapped[str | None] = mapped_column(String(255))

    category_rel: Mapped["Category"] = relationship(back_populates="products")
    items: Mapped[list["Item"]] = relationship(back_populates="product")


class Supplier(Base):
    __tablename__ = "supplier"

    suppid: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(2), nullable=False)
    addr1: Mapped[str | None] = mapped_column(String(80))
    addr2: Mapped[str | None] = mapped_column(String(80))
    city: Mapped[str | None] = mapped_column(String(80))
    state: Mapped[str | None] = mapped_column(String(80))
    zip: Mapped[str | None] = mapped_column(String(5))
    phone: Mapped[str | None] = mapped_column(String(80))

    items: Mapped[list["Item"]] = relationship(back_populates="supplier_rel")


class Item(Base):
    __tablename__ = "item"
    __table_args__ = (Index("itemProd", "productid"),)

    itemid: Mapped[str] = mapped_column(String(10), primary_key=True)
    productid: Mapped[str] = mapped_column(
        String(10), ForeignKey("product.productid"), nullable=False
    )
    listprice: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    unitcost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    supplier: Mapped[int | None] = mapped_column(Integer, ForeignKey("supplier.suppid"))
    status: Mapped[str | None] = mapped_column(String(2))
    attr1: Mapped[str | None] = mapped_column(String(80))
    attr2: Mapped[str | None] = mapped_column(String(80))
    attr3: Mapped[str | None] = mapped_column(String(80))
    attr4: Mapped[str | None] = mapped_column(String(80))
    attr5: Mapped[str | None] = mapped_column(String(80))

    product: Mapped["Product"] = relationship(back_populates="items")
    supplier_rel: Mapped["Supplier | None"] = relationship(back_populates="items")


class Inventory(Base):
    """Legacy schema has no FK from inventory.itemid to item.itemid."""

    __tablename__ = "inventory"
    __table_args__ = (CheckConstraint("qty >= 0", name="ck_inventory_qty_non_negative"),)

    itemid: Mapped[str] = mapped_column(String(10), primary_key=True)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)


class BannerData(Base):
    __tablename__ = "bannerdata"

    favcategory: Mapped[str] = mapped_column(String(80), primary_key=True)
    bannername: Mapped[str | None] = mapped_column(String(255))
