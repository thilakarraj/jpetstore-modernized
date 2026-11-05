"""Cart business logic."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from jpetstore.core.exceptions import AppError
from jpetstore.models import Inventory
from jpetstore.modules.account.service import AuthUser
from jpetstore.modules.cart.pricing import line_total, money, sum_lines
from jpetstore.modules.cart.repository import CartRepository
from jpetstore.modules.cart.schemas import (
    AddCartItemRequest,
    CartLineResponse,
    CartResponse,
    UpdateCartItemRequest,
)


class CartService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = CartRepository(session)

    def add_item(self, user: AuthUser, payload: AddCartItemRequest) -> CartResponse:
        if self._repo.get_catalog_item(payload.item_id) is None:
            raise AppError(
                code="ITEM_NOT_FOUND",
                message="Invalid item id.",
                status_code=400,
            )
        try:
            cart = self._repo.get_or_create_active_cart(user.username)
            self._repo.add_or_increment_item(cart.cart_id, payload.item_id, payload.quantity)
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
        return self.get_cart(user)

    def get_cart(self, user: AuthUser) -> CartResponse:
        cart = self._repo.get_active_cart_with_items(user.username)
        if cart is None:
            return CartResponse(cart_id=0, lines=[], sub_total=Decimal("0.00"))
        return self._build_response(cart)

    def update_item(
        self,
        user: AuthUser,
        item_id: str,
        payload: UpdateCartItemRequest,
    ) -> CartResponse:
        cart = self._repo.get_active_cart_for_user(user.username)
        if cart is None:
            raise AppError(
                code="CART_LINE_NOT_FOUND",
                message="Cart line not found.",
                status_code=404,
            )
        line = self._repo.update_item_quantity(cart.cart_id, item_id, payload.quantity)
        if line is None:
            raise AppError(
                code="CART_LINE_NOT_FOUND",
                message="Cart line not found.",
                status_code=404,
            )
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
        return self.get_cart(user)

    def remove_item(self, user: AuthUser, item_id: str) -> CartResponse:
        cart = self._repo.get_active_cart_for_user(user.username)
        if cart is None:
            raise AppError(
                code="CART_LINE_NOT_FOUND",
                message="Cart line not found.",
                status_code=404,
            )
        removed = self._repo.remove_item(cart.cart_id, item_id)
        if not removed:
            raise AppError(
                code="CART_LINE_NOT_FOUND",
                message="Cart line not found.",
                status_code=404,
            )
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
        return self.get_cart(user)

    def clear_cart(self, user: AuthUser) -> CartResponse:
        cart = self._repo.get_active_cart_for_user(user.username)
        if cart is not None:
            self._repo.clear_items(cart.cart_id)
            try:
                self._session.commit()
            except Exception:
                self._session.rollback()
                raise
        return CartResponse(cart_id=cart.cart_id if cart else 0, lines=[], sub_total=Decimal("0.00"))

    def _build_response(self, cart) -> CartResponse:
        lines: list[CartLineResponse] = []
        line_totals: list[Decimal | None] = []
        for row in cart.items:
            catalog_item = self._repo.get_catalog_item(row.itemid)
            if catalog_item is None:
                lines.append(
                    CartLineResponse(
                        item_id=row.itemid,
                        quantity=row.quantity,
                        item_available=False,
                        in_stock=False,
                        list_price=None,
                        line_total=None,
                    )
                )
                line_totals.append(None)
                continue
            inv = self._session.get(Inventory, row.itemid)
            qty_on_hand = inv.qty if inv is not None else 0
            unit = money(catalog_item.listprice)
            total = line_total(unit, row.quantity)
            lines.append(
                CartLineResponse(
                    item_id=row.itemid,
                    product_id=catalog_item.productid,
                    product_name=catalog_item.product.name if catalog_item.product else None,
                    quantity=row.quantity,
                    list_price=unit,
                    line_total=total,
                    in_stock=qty_on_hand > 0,
                    item_available=True,
                )
            )
            line_totals.append(total)
        return CartResponse(
            cart_id=cart.cart_id,
            lines=lines,
            sub_total=sum_lines(line_totals),
        )
