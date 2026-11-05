"""FastAPI dependencies for the account module."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from jpetstore.config import Settings, get_settings
from jpetstore.core.database import get_db_session
from jpetstore.core.exceptions import AppError
from jpetstore.core.rate_limit import get_rate_limiter
from jpetstore.modules.account.security import decode_access_token
from jpetstore.modules.account.service import AccountService, AuthUser
from jpetstore.security.audit import audit_event

_bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def get_account_service(session: DbSession) -> AccountService:
    return AccountService(session)


AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def enforce_login_rate_limit(request: Request, settings: AppSettings) -> None:
    key = f"login:{_client_ip(request)}"
    if get_rate_limiter().allow(key, limit=settings.rate_limit_login_per_minute):
        return
    audit_event(
        request,
        event="auth.rate_limit",
        outcome="failure",
        failure_category="login",
    )
    raise AppError(
        code="RATE_LIMIT_EXCEEDED",
        message="Too many requests. Please try again later.",
        status_code=429,
    )


def enforce_register_rate_limit(request: Request, settings: AppSettings) -> None:
    key = f"register:{_client_ip(request)}"
    if get_rate_limiter().allow(key, limit=settings.rate_limit_register_per_minute):
        return
    audit_event(
        request,
        event="auth.rate_limit",
        outcome="failure",
        failure_category="register",
    )
    raise AppError(
        code="RATE_LIMIT_EXCEEDED",
        message="Too many requests. Please try again later.",
        status_code=429,
    )


def get_current_user(
    request: Request,
    settings: AppSettings,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> AuthUser:
    if credentials is None:
        audit_event(
            request,
            event="auth.token",
            outcome="failure",
            failure_category="missing_authorization",
        )
        raise AppError(
            code="UNAUTHORIZED",
            message="Authentication required.",
            status_code=401,
        )
    if credentials.scheme.lower() != "bearer":
        audit_event(
            request,
            event="auth.token",
            outcome="failure",
            failure_category="invalid_scheme",
        )
        raise AppError(
            code="UNAUTHORIZED",
            message="Invalid authorization scheme.",
            status_code=401,
        )
    try:
        username = decode_access_token(credentials.credentials, settings)
    except AppError:
        audit_event(
            request,
            event="auth.token",
            outcome="failure",
            failure_category="invalid_token",
        )
        raise
    return AuthUser(username=username)


CurrentUser = Annotated[AuthUser, Depends(get_current_user)]
