"""Security audit logging helpers."""

from __future__ import annotations

from typing import Any

from fastapi import Request

from jpetstore.logging_setup import get_security_logger

SECURITY_LOGGER = get_security_logger()


def audit_event(
    request: Request,
    *,
    event: str,
    outcome: str,
    user_identifier: str | None = None,
    failure_category: str | None = None,
) -> None:
    """Write a structured line to security-audit.log (no secrets)."""
    extra: dict[str, Any] = {
        "event": event,
        "outcome": outcome,
        "request_id": getattr(request.state, "request_id", None),
        "method": request.method,
        "route": request.url.path,
    }
    if user_identifier:
        extra["user_identifier"] = user_identifier
    if failure_category:
        extra["failure_category"] = failure_category
    SECURITY_LOGGER.info("security audit", extra=extra)
