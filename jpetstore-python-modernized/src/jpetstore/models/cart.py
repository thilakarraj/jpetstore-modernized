"""Persistent shopping cart ORM models."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jpetstore.models.base import Base

if TYPE_CHECKING:
    from jpetstore.models.cart import CartItem


class Cart(Base):
    __tablename__ = "cart"
    __table_args__ = (
        Index("ix_cart_userid", "userid"),
        UniqueConstraint("userid", name="uq_cart_userid"),
    )

    cart_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userid: Mapped[str] = mapped_column(
        String(80), ForeignKey("account.userid", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart",
        cascade="all, delete-orphan",
    )


class CartItem(Base):
    __tablename__ = "cart_item"
    __table_args__ = (
        UniqueConstraint("cart_id", "itemid", name="uq_cart_item_cart_itemid"),
        CheckConstraint("quantity > 0", name="ck_cart_item_quantity_positive"),
        Index("ix_cart_item_cart_id", "cart_id"),
        Index("ix_cart_item_itemid", "itemid"),
    )

    cart_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cart.cart_id", ondelete="CASCADE"), nullable=False
    )
    itemid: Mapped[str] = mapped_column(
        String(10), ForeignKey("item.itemid"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    cart: Mapped["Cart"] = relationship(back_populates="items")
