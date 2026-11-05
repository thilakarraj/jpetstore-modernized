"""Checkout and order business logic."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from jpetstore.models import LineItem, Order, OrderStatus
from jpetstore.modules.account.service import AuthUser
from jpetstore.modules.cart.repository import CartRepository
from jpetstore.modules.cart.pricing import money
from jpetstore.modules.order.idempotency import checkout_fingerprint
from jpetstore.modules.order.pricing import mask_card_for_response, mask_card_last_four, order_line_total
from jpetstore.modules.order.repository import OrderRepository
from jpetstore.modules.order.schemas import (
    CheckoutRequest,
    CheckoutResponse,
    OrderDetailResponse,
    OrderLineResponse,
    OrderListResponse,
    OrderSummaryResponse,
)
from jpetstore.core.exceptions import AppError

EMPTY_CART_MESSAGE = "An order could not be created because a cart could not be found."
INITIAL_ORDER_STATUS = "P"


class OrderService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._orders = OrderRepository(session)
        self._cart = CartRepository(session)

    def checkout(
        self,
        user: AuthUser,
        idempotency_key: str,
        payload: CheckoutRequest,
    ) -> CheckoutResponse:
        key = idempotency_key.strip()
        if not key or len(key) > 128:
            raise AppError(
                code="IDEMPOTENCY_KEY_REQUIRED",
                message="Idempotency-Key header is required.",
                status_code=400,
            )
        fingerprint = checkout_fingerprint(payload)

        try:
            existing = self._orders.get_idempotency(user.username, key, for_update=True)
            if existing is not None:
                if existing.request_fingerprint != fingerprint:
                    raise AppError(
                        code="IDEMPOTENCY_CONFLICT",
                        message="Idempotency key reused with a different request.",
                        status_code=409,
                    )
                if existing.orderid is not None:
                    order = self._build_detail(existing.orderid, user)
                    return CheckoutResponse(
                        order_id=existing.orderid,
                        order=order,
                        idempotent_replay=True,
                    )

            if existing is None:
                try:
                    existing = self._orders.add_idempotency(user.username, key, fingerprint)
                except IntegrityError:
                    self._session.rollback()
                    existing = self._orders.get_idempotency(user.username, key, for_update=True)
                    if existing is None:
                        raise
                    if existing.request_fingerprint != fingerprint:
                        raise AppError(
                            code="IDEMPOTENCY_CONFLICT",
                            message="Idempotency key reused with a different request.",
                            status_code=409,
                        ) from None
                    if existing.orderid is not None:
                        order = self._build_detail(existing.orderid, user)
                        return CheckoutResponse(
                            order_id=existing.orderid,
                            order=order,
                            idempotent_replay=True,
                        )

            cart = self._cart.get_active_cart_for_update(user.username)
            if cart is None or not cart.items:
                raise AppError(
                    code="CART_EMPTY",
                    message=EMPTY_CART_MESSAGE,
                    status_code=400,
                )

            priced_lines: list[tuple[str, int, Decimal]] = []
            for cart_line in cart.items:
                item = self._orders.get_item(cart_line.itemid)
                if item is None:
                    raise AppError(
                        code="INVALID_CART_ITEM",
                        message=f"Cart item {cart_line.itemid} is no longer available.",
                        status_code=400,
                    )
                if item.listprice is None:
                    raise AppError(
                        code="INVALID_CART_ITEM",
                        message=f"Item {cart_line.itemid} has no price.",
                        status_code=400,
                    )
                unit = money(item.listprice)
                assert unit is not None
                priced_lines.append((cart_line.itemid, cart_line.quantity, unit))

            seq = self._orders.lock_sequence("ordernum")
            order_id = seq.nextid
            seq.nextid = order_id + 1

            subtotal = Decimal("0.00")
            for _itemid, qty, unit in priced_lines:
                subtotal += order_line_total(unit, qty)

            today = datetime.now(tz=UTC).date()
            stored_card = mask_card_last_four(payload.card_last_four)

            order = Order(
                orderid=order_id,
                userid=user.username,
                orderdate=today,
                shipaddr1=payload.ship_address1,
                shipaddr2=payload.ship_address2,
                shipcity=payload.ship_city,
                shipstate=payload.ship_state,
                shipzip=payload.ship_zip,
                shipcountry=payload.ship_country,
                billaddr1=payload.bill_address1,
                billaddr2=payload.bill_address2,
                billcity=payload.bill_city,
                billstate=payload.bill_state,
                billzip=payload.bill_zip,
                billcountry=payload.bill_country,
                courier=payload.courier,
                totalprice=subtotal,
                billtofirstname=payload.bill_to_first_name,
                billtolastname=payload.bill_to_last_name,
                shiptofirstname=payload.ship_to_first_name,
                shiptolastname=payload.ship_to_last_name,
                creditcard=stored_card,
                exprdate=payload.expiry_date,
                cardtype=payload.card_type,
                locale=payload.locale,
            )
            self._orders.add_order(order)
            self._orders.add_order_status(
                OrderStatus(
                    orderid=order_id,
                    linenum=1,
                    timestamp=today,
                    status=INITIAL_ORDER_STATUS,
                )
            )

            for index, (itemid, qty, unit) in enumerate(priced_lines, start=1):
                self._orders.add_line_item(
                    LineItem(
                        orderid=order_id,
                        linenum=index,
                        itemid=itemid,
                        quantity=qty,
                        unitprice=unit,
                    )
                )

            for _itemid, qty, _unit in priced_lines:
                inv = self._orders.lock_inventory(_itemid)
                if inv is None or inv.qty < qty:
                    raise AppError(
                        code="INSUFFICIENT_INVENTORY",
                        message=f"Insufficient inventory for item {_itemid}.",
                        status_code=400,
                    )
                inv.qty -= qty

            self._cart.complete_checkout(cart)
            self._orders.attach_order_to_idempotency(existing, order_id)
            self._session.commit()
        except AppError:
            self._session.rollback()
            raise
        except SQLAlchemyError as exc:
            self._session.rollback()
            raise AppError(
                code="TRANSACTION_FAILED",
                message="Order could not be completed. Please try again.",
                status_code=503,
            ) from exc

        detail = self._build_detail(order_id, user)
        return CheckoutResponse(order_id=order_id, order=detail)

    def list_orders(self, user: AuthUser) -> OrderListResponse:
        orders = self._orders.list_orders_for_user(user.username)
        summaries: list[OrderSummaryResponse] = []
        for order in orders:
            status_row = self._orders.get_latest_status(order.orderid)
            summaries.append(
                OrderSummaryResponse(
                    order_id=order.orderid,
                    order_date=order.orderdate,
                    total_price=order.totalprice,
                    status=status_row.status if status_row else INITIAL_ORDER_STATUS,
                )
            )
        return OrderListResponse(orders=summaries)

    def get_order(self, user: AuthUser, order_id: int) -> OrderDetailResponse:
        order = self._orders.get_order(order_id)
        if order is None or order.userid != user.username:
            raise AppError(
                code="ORDER_FORBIDDEN",
                message="You may only view your own orders.",
                status_code=403,
            )
        return self._build_detail(order_id, user)

    def _build_detail(self, order_id: int, user: AuthUser) -> OrderDetailResponse:
        order = self._orders.get_order(order_id)
        if order is None or order.userid != user.username:
            raise AppError(
                code="ORDER_FORBIDDEN",
                message="You may only view your own orders.",
                status_code=403,
            )
        status_row = self._orders.get_latest_status(order_id)
        lines_db = self._orders.list_line_items(order_id)
        lines = [
            OrderLineResponse(
                line_number=line.linenum,
                item_id=line.itemid,
                quantity=line.quantity,
                unit_price=line.unitprice,
                line_total=order_line_total(line.unitprice, line.quantity),
            )
            for line in lines_db
        ]
        return OrderDetailResponse(
            order_id=order.orderid,
            order_date=order.orderdate,
            total_price=order.totalprice,
            status=status_row.status if status_row else INITIAL_ORDER_STATUS,
            courier=order.courier,
            locale=order.locale,
            card_type=order.cardtype,
            card_display=mask_card_for_response(order.creditcard),
            expiry_date=order.exprdate,
            ship_to_first_name=order.shiptofirstname,
            ship_to_last_name=order.shiptolastname,
            ship_address1=order.shipaddr1,
            ship_address2=order.shipaddr2,
            ship_city=order.shipcity,
            ship_state=order.shipstate,
            ship_zip=order.shipzip,
            ship_country=order.shipcountry,
            bill_to_first_name=order.billtofirstname,
            bill_to_last_name=order.billtolastname,
            bill_address1=order.billaddr1,
            bill_address2=order.billaddr2,
            bill_city=order.billcity,
            bill_state=order.billstate,
            bill_zip=order.billzip,
            bill_country=order.billcountry,
            lines=lines,
        )
