"""Account and authentication HTTP routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from jpetstore.core.exceptions import AppError
from jpetstore.metrics.prometheus import AUTH_LOGIN_ATTEMPTS_TOTAL, AUTH_REGISTRATION_TOTAL
from jpetstore.modules.account.dependencies import (
    AccountServiceDep,
    AppSettings,
    CurrentUser,
    enforce_login_rate_limit,
    enforce_register_rate_limit,
)
from jpetstore.modules.catalog.dependencies import CatalogServiceDep
from jpetstore.modules.catalog.schemas import ProductListResponse
from jpetstore.modules.account.schemas import (
    AccountProfileResponse,
    AccountUpdateRequest,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from jpetstore.security.audit import audit_event

router = APIRouter(prefix="/api/v1", tags=["account"])


@router.post(
    "/auth/register",
    response_model=RegisterResponse,
    status_code=201,
    dependencies=[Depends(enforce_register_rate_limit)],
)
def register(
    request: Request,
    payload: RegisterRequest,
    service: AccountServiceDep,
) -> RegisterResponse:
    try:
        result = service.register(payload)
    except AppError as exc:
        outcome = "failure"
        if exc.code == "USERNAME_EXISTS":
            AUTH_REGISTRATION_TOTAL.labels(outcome=outcome).inc()
            audit_event(
                request,
                event="auth.register",
                outcome=outcome,
                user_identifier=payload.username,
                failure_category="duplicate_username",
            )
        else:
            AUTH_REGISTRATION_TOTAL.labels(outcome=outcome).inc()
            audit_event(
                request,
                event="auth.register",
                outcome=outcome,
                user_identifier=payload.username,
            )
        raise
    AUTH_REGISTRATION_TOTAL.labels(outcome="success").inc()
    audit_event(
        request,
        event="auth.register",
        outcome="success",
        user_identifier=result.username,
    )
    return result


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    dependencies=[Depends(enforce_login_rate_limit)],
)
def login(
    request: Request,
    payload: LoginRequest,
    service: AccountServiceDep,
    settings: AppSettings,
) -> TokenResponse:
    try:
        token = service.login(payload.username, payload.password, settings)
    except AppError as exc:
        AUTH_LOGIN_ATTEMPTS_TOTAL.labels(outcome="failure").inc()
        audit_event(
            request,
            event="auth.login",
            outcome="failure",
            user_identifier=payload.username,
            failure_category="invalid_credentials",
        )
        raise
    AUTH_LOGIN_ATTEMPTS_TOTAL.labels(outcome="success").inc()
    audit_event(
        request,
        event="auth.login",
        outcome="success",
        user_identifier=payload.username,
    )
    return token


@router.get("/account/me", response_model=AccountProfileResponse)
def get_me(
    request: Request,
    user: CurrentUser,
    service: AccountServiceDep,
) -> AccountProfileResponse:
    profile = service.get_profile(user)
    audit_event(
        request,
        event="account.read",
        outcome="success",
        user_identifier=user.username,
    )
    return profile


@router.put("/account/me", response_model=AccountProfileResponse)
def update_me(
    request: Request,
    payload: AccountUpdateRequest,
    user: CurrentUser,
    service: AccountServiceDep,
) -> AccountProfileResponse:
    try:
        updated = service.update_profile(user, payload)
    except AppError as exc:
        audit_event(
            request,
            event="account.update",
            outcome="failure",
            user_identifier=user.username,
            failure_category=exc.code.lower(),
        )
        raise
    audit_event(
        request,
        event="account.update",
        outcome="success",
        user_identifier=user.username,
    )
    return updated


@router.get("/account/me/my-list", response_model=ProductListResponse)
def get_my_list(
    user: CurrentUser,
    account_service: AccountServiceDep,
    catalog_service: CatalogServiceDep,
) -> ProductListResponse:
    profile = account_service.get_profile(user)
    return catalog_service.my_list_products(profile.favourite_category_id)
