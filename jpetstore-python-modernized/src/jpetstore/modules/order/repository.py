"""Order and checkout persistence."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from jpetstore.models import (
    CheckoutIdempotency,
    Inventory,
    Item,
    LineItem,
    Order,
    OrderStatus,
    Sequence,
)


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_idempotency(
        self, userid: str, idempotency_key: str, *, for_update: bool = False
    ) -> CheckoutIdempotency | None:
        stmt = select(CheckoutIdempotency).where(
            CheckoutIdempotency.userid == userid,
            CheckoutIdempotency.idempotency_key == idempotency_key,
        )
        if for_update:
            stmt = stmt.with_for_update()
        return self._session.scalar(stmt)

    def add_idempotency(
        self, userid: str, idempotency_key: str, fingerprint: str
    ) -> CheckoutIdempotency:
        row = CheckoutIdempotency(
            userid=userid,
            idempotency_key=idempotency_key,
            request_fingerprint=fingerprint,
            orderid=None,
        )
        self._session.add(row)
        self._session.flush()
        return row

    def attach_order_to_idempotency(self, row: CheckoutIdempotency, orderid: int) -> None:
        row.orderid = orderid
        self._session.flush()

    def lock_sequence(self, name: str = "ordernum") -> Sequence:
        seq = self._session.scalar(
            select(Sequence).where(Sequence.name == name).with_for_update()
        )
        if seq is None:
            raise LookupError(f"Sequence {name} not found")
        return seq

    def lock_inventory(self, itemid: str) -> Inventory | None:
        return self._session.scalar(
            select(Inventory).where(Inventory.itemid == itemid).with_for_update()
        )

    def get_item(self, itemid: str) -> Item | None:
        return self._session.get(Item, itemid)

    def add_order(self, order: Order) -> Order:
        self._session.add(order)
        self._session.flush()
        return order

    def add_order_status(self, status_row: OrderStatus) -> None:
        self._session.add(status_row)
        self._session.flush()

    def add_line_item(self, line: LineItem) -> None:
        self._session.add(line)
        self._session.flush()

    def list_orders_for_user(self, userid: str) -> list[Order]:
        return list(
            self._session.scalars(
                select(Order).where(Order.userid == userid).order_by(Order.orderid.desc())
            ).all()
        )

    def get_order(self, orderid: int) -> Order | None:
        return self._session.get(Order, orderid)

    def get_order_with_lines(self, orderid: int) -> Order | None:
        order = self.get_order(orderid)
        if order is None:
            return None
        _ = list(
            self._session.scalars(
                select(LineItem).where(LineItem.orderid == orderid).order_by(LineItem.linenum)
            ).all()
        )
        return order

    def get_latest_status(self, orderid: int) -> OrderStatus | None:
        return self._session.scalar(
            select(OrderStatus)
            .where(OrderStatus.orderid == orderid)
            .order_by(OrderStatus.linenum.desc())
            .limit(1)
        )

    def list_line_items(self, orderid: int) -> list[LineItem]:
        return list(
            self._session.scalars(
                select(LineItem).where(LineItem.orderid == orderid).order_by(LineItem.linenum)
            ).all()
        )
