"""HTTP request/response logging middleware."""

import time
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from jpetstore.logging_setup import get_logger
from jpetstore.metrics.prometheus import normalize_route

logger = get_logger("http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start = time.perf_counter()
        route = normalize_route(request.url.path)
        method = request.method
        request_id = getattr(request.state, "request_id", None)
        status_code = 500
        response: Response | None = None
        try:
            response = await call_next(request)
            status_code = response.status_code
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                "HTTP request completed",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "route": route,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                },
            )
        assert response is not None
        return response
