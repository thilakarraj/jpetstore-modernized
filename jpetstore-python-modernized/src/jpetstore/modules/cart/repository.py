"""Cart persistence."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from jpetstore.models import Cart, CartItem, Item


class CartRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_active_cart_for_user(self, userid: str) -> Cart | None:
        return self._session.scalar(
            select(Cart).where(Cart.userid == userid, Cart.status == "active")
        )

    def get_active_cart_with_items(self, userid: str) -> Cart | None:
        return self._session.scalar(
            select(Cart)
            .where(Cart.userid == userid, Cart.status == "active")
            .options(joinedload(Cart.items))
        )

    def create_active_cart(self, userid: str) -> Cart:
        cart = Cart(userid=userid, status="active")
        self._session.add(cart)
        self._session.flush()
        return cart

    def get_or_create_active_cart(self, userid: str) -> Cart:
        """One cart row per user; reactivate after checkout."""
        existing = self.get_active_cart_for_user(userid)
        if existing is not None:
            return existing
        prior = self._session.scalar(select(Cart).where(Cart.userid == userid))
        if prior is not None and prior.status == "checked_out":
            prior.status = "active"
            self._session.flush()
            return prior
        nested = self._session.begin_nested()
        try:
            cart = self.create_active_cart(userid)
            nested.commit()
            return cart
        except IntegrityError:
            nested.rollback()
            cart = self.get_active_cart_for_user(userid)
            if cart is None:
                raise
            return cart

    def get_cart_item(self, cart_id: int, itemid: str) -> CartItem | None:
        return self._session.scalar(
            select(CartItem).where(CartItem.cart_id == cart_id, CartItem.itemid == itemid)
        )

    def add_or_increment_item(self, cart_id: int, itemid: str, quantity: int) -> CartItem:
        line = self.get_cart_item(cart_id, itemid)
        if line is not None:
            line.quantity += quantity
            self._session.flush()
            return line
        line = CartItem(cart_id=cart_id, itemid=itemid, quantity=quantity)
        self._session.add(line)
        nested = self._session.begin_nested()
        try:
            self._session.flush()
            nested.commit()
            return line
        except IntegrityError:
            nested.rollback()
            existing = self.get_cart_item(cart_id, itemid)
            if existing is None:
                raise
            existing.quantity += quantity
            self._session.flush()
            return existing

    def update_item_quantity(self, cart_id: int, itemid: str, quantity: int) -> CartItem | None:
        line = self.get_cart_item(cart_id, itemid)
        if line is None:
            return None
        line.quantity = quantity
        self._session.flush()
        return line

    def remove_item(self, cart_id: int, itemid: str) -> bool:
        line = self.get_cart_item(cart_id, itemid)
        if line is None:
            return False
        self._session.delete(line)
        self._session.flush()
        return True

    def clear_items(self, cart_id: int) -> None:
        for line in list(
            self._session.scalars(select(CartItem).where(CartItem.cart_id == cart_id)).all()
        ):
            self._session.delete(line)
        self._session.flush()

    def get_catalog_item(self, itemid: str) -> Item | None:
        return self._session.scalar(
            select(Item).where(Item.itemid == itemid).options(joinedload(Item.product))
        )

    def verify_cart_owner(self, cart_id: int, userid: str) -> bool:
        cart = self._session.get(Cart, cart_id)
        return cart is not None and cart.userid == userid and cart.status == "active"

    def get_active_cart_for_update(self, userid: str) -> Cart | None:
        return self._session.scalar(
            select(Cart)
            .where(Cart.userid == userid, Cart.status == "active")
            .options(joinedload(Cart.items))
            .with_for_update()
        )

    def complete_checkout(self, cart: Cart) -> None:
        self.clear_items(cart.cart_id)
        cart.status = "checked_out"
        self._session.flush()
