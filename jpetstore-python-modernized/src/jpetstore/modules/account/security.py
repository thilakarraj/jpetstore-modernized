"""JWT creation and validation for the account module."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from jpetstore.config import Settings
from jpetstore.core.exceptions import AppError


def create_access_token(subject: str, settings: Settings) -> tuple[str, int]:
    expires_seconds = settings.jwt_expire_minutes * 60
    now = datetime.now(tz=UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_seconds)).timestamp()),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires_seconds


def decode_access_token(token: str, settings: Settings) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except JWTError as exc:
        raise AppError(
            code="INVALID_TOKEN",
            message="Invalid or expired access token.",
            status_code=401,
        ) from exc
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise AppError(
            code="INVALID_TOKEN",
            message="Invalid or expired access token.",
            status_code=401,
        )
    return subject
