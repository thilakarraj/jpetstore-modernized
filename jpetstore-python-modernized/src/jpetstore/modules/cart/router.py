"""Cart HTTP routes (JWT required)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from jpetstore.core.exceptions import AppError
from jpetstore.metrics.prometheus import (
    CART_ADD_TOTAL,
    CART_REMOVE_TOTAL,
    CART_UPDATE_TOTAL,
)
from jpetstore.modules.account.dependencies import CurrentUser
from jpetstore.modules.cart.dependencies import CartServiceDep
from jpetstore.modules.cart.schemas import (
    AddCartItemRequest,
    CartResponse,
    UpdateCartItemRequest,
)
from jpetstore.security.audit import audit_event

router = APIRouter(prefix="/api/v1/cart", tags=["cart"])


@router.post("/items", response_model=CartResponse)
def add_cart_item(
    request: Request,
    payload: AddCartItemRequest,
    user: CurrentUser,
    service: CartServiceDep,
) -> CartResponse:
    try:
        cart = service.add_item(user, payload)
    except AppError as exc:
        CART_ADD_TOTAL.labels(outcome="failure").inc()
        audit_event(
            request,
            event="cart.add",
            outcome="failure",
            user_identifier=user.username,
            failure_category=exc.code.lower(),
        )
        raise
    CART_ADD_TOTAL.labels(outcome="success").inc()
    audit_event(
        request,
        event="cart.add",
        outcome="success",
        user_identifier=user.username,
    )
    return cart


@router.get("", response_model=CartResponse)
def get_cart(
    request: Request,
    user: CurrentUser,
    service: CartServiceDep,
) -> CartResponse:
    cart = service.get_cart(user)
    audit_event(
        request,
        event="cart.read",
        outcome="success",
        user_identifier=user.username,
    )
    return cart


@router.put("/items/{item_id}", response_model=CartResponse)
def update_cart_item(
    request: Request,
    item_id: str,
    payload: UpdateCartItemRequest,
    user: CurrentUser,
    service: CartServiceDep,
) -> CartResponse:
    try:
        cart = service.update_item(user, item_id, payload)
    except AppError as exc:
        CART_UPDATE_TOTAL.labels(outcome="failure").inc()
        audit_event(
            request,
            event="cart.update",
            outcome="failure",
            user_identifier=user.username,
            failure_category=exc.code.lower(),
        )
        raise
    CART_UPDATE_TOTAL.labels(outcome="success").inc()
    audit_event(
        request,
        event="cart.update",
        outcome="success",
        user_identifier=user.username,
    )
    return cart


@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_cart_item(
    request: Request,
    item_id: str,
    user: CurrentUser,
    service: CartServiceDep,
) -> CartResponse:
    try:
        cart = service.remove_item(user, item_id)
    except AppError as exc:
        CART_REMOVE_TOTAL.labels(outcome="failure").inc()
        audit_event(
            request,
            event="cart.remove",
            outcome="failure",
            user_identifier=user.username,
            failure_category=exc.code.lower(),
        )
        raise
    CART_REMOVE_TOTAL.labels(outcome="success").inc()
    audit_event(
        request,
        event="cart.remove",
        outcome="success",
        user_identifier=user.username,
    )
    return cart


@router.delete("", response_model=CartResponse)
def clear_cart(
    request: Request,
    user: CurrentUser,
    service: CartServiceDep,
) -> CartResponse:
    cart = service.clear_cart(user)
    audit_event(
        request,
        event="cart.clear",
        outcome="success",
        user_identifier=user.username,
    )
    CART_REMOVE_TOTAL.labels(outcome="success").inc()
    return cart
