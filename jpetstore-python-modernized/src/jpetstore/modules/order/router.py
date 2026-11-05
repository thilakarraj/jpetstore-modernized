"""Order module HTTP routes."""

from __future__ import annotations

from fastapi import APIRouter, Header, Request, Response

from jpetstore.core.exceptions import AppError
from jpetstore.metrics.prometheus import ORDERS_CREATED_TOTAL
from jpetstore.modules.account.dependencies import CurrentUser
from jpetstore.modules.order.dependencies import OrderServiceDep
from jpetstore.modules.order.schemas import (
    CheckoutRequest,
    CheckoutResponse,
    OrderDetailResponse,
    OrderListResponse,
)
from jpetstore.security.audit import audit_event

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    request: Request,
    payload: CheckoutRequest,
    user: CurrentUser,
    service: OrderServiceDep,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> CheckoutResponse:
    audit_event(
        request,
        event="order.checkout",
        outcome="started",
        user_identifier=user.username,
    )
    try:
        result = service.checkout(user, idempotency_key or "", payload)
    except AppError as exc:
        ORDERS_CREATED_TOTAL.labels(outcome="failure").inc()
        category = exc.code.lower()
        audit_event(
            request,
            event="order.checkout",
            outcome="failure",
            user_identifier=user.username,
            failure_category=category,
        )
        if exc.code == "IDEMPOTENCY_CONFLICT":
            audit_event(
                request,
                event="order.idempotency",
                outcome="failure",
                user_identifier=user.username,
                failure_category="conflict",
            )
        if exc.code == "INSUFFICIENT_INVENTORY":
            audit_event(
                request,
                event="order.inventory",
                outcome="failure",
                user_identifier=user.username,
            )
        raise
    ORDERS_CREATED_TOTAL.labels(outcome="success").inc()
    audit_event(
        request,
        event="order.checkout",
        outcome="success",
        user_identifier=user.username,
    )
    if result.idempotent_replay:
        response.status_code = 200
    else:
        response.status_code = 201
    return result


@router.get("", response_model=OrderListResponse)
def list_orders(
    request: Request,
    user: CurrentUser,
    service: OrderServiceDep,
) -> OrderListResponse:
    orders = service.list_orders(user)
    audit_event(
        request,
        event="order.list",
        outcome="success",
        user_identifier=user.username,
    )
    return orders


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order(
    request: Request,
    order_id: int,
    user: CurrentUser,
    service: OrderServiceDep,
) -> OrderDetailResponse:
    try:
        order = service.get_order(user, order_id)
    except AppError as exc:
        if exc.code == "ORDER_FORBIDDEN":
            audit_event(
                request,
                event="order.read",
                outcome="failure",
                user_identifier=user.username,
                failure_category="forbidden",
            )
        raise
    audit_event(
        request,
        event="order.read",
        outcome="success",
        user_identifier=user.username,
    )
    return order
