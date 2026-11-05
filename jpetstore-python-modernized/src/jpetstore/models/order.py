"""Order domain ORM models."""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from jpetstore.models.base import Base


class Order(Base):
    __tablename__ = "orders"

    orderid: Mapped[int] = mapped_column(Integer, primary_key=True)
    userid: Mapped[str] = mapped_column(String(80), nullable=False)
    orderdate: Mapped[date] = mapped_column(Date, nullable=False)
    shipaddr1: Mapped[str] = mapped_column(String(80), nullable=False)
    shipaddr2: Mapped[str | None] = mapped_column(String(80))
    shipcity: Mapped[str] = mapped_column(String(80), nullable=False)
    shipstate: Mapped[str] = mapped_column(String(80), nullable=False)
    shipzip: Mapped[str] = mapped_column(String(20), nullable=False)
    shipcountry: Mapped[str] = mapped_column(String(20), nullable=False)
    billaddr1: Mapped[str] = mapped_column(String(80), nullable=False)
    billaddr2: Mapped[str | None] = mapped_column(String(80))
    billcity: Mapped[str] = mapped_column(String(80), nullable=False)
    billstate: Mapped[str] = mapped_column(String(80), nullable=False)
    billzip: Mapped[str] = mapped_column(String(20), nullable=False)
    billcountry: Mapped[str] = mapped_column(String(20), nullable=False)
    courier: Mapped[str] = mapped_column(String(80), nullable=False)
    totalprice: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    billtofirstname: Mapped[str] = mapped_column(String(80), nullable=False)
    billtolastname: Mapped[str] = mapped_column(String(80), nullable=False)
    shiptofirstname: Mapped[str] = mapped_column(String(80), nullable=False)
    shiptolastname: Mapped[str] = mapped_column(String(80), nullable=False)
    creditcard: Mapped[str] = mapped_column(String(80), nullable=False)
    exprdate: Mapped[str] = mapped_column(String(7), nullable=False)
    cardtype: Mapped[str] = mapped_column(String(80), nullable=False)
    locale: Mapped[str] = mapped_column(String(80), nullable=False)


class OrderStatus(Base):
    __tablename__ = "orderstatus"

    orderid: Mapped[int] = mapped_column(Integer, primary_key=True)
    linenum: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(2), nullable=False)


class LineItem(Base):
    """Legacy schema: no FK from lineitem.itemid to item.itemid."""

    __tablename__ = "lineitem"

    orderid: Mapped[int] = mapped_column(Integer, primary_key=True)
    linenum: Mapped[int] = mapped_column(Integer, primary_key=True)
    itemid: Mapped[str] = mapped_column(String(10), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unitprice: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


class Sequence(Base):
    __tablename__ = "sequence"

    name: Mapped[str] = mapped_column(String(30), primary_key=True)
    nextid: Mapped[int] = mapped_column(Integer, nullable=False)
