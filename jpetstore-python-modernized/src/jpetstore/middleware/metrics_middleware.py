"""Prometheus instrumentation middleware."""

import time
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from jpetstore.metrics.prometheus import (
    HTTP_ERRORS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_IN_PROGRESS,
    HTTP_REQUESTS_TOTAL,
    METRICS_ROUTE,
    normalize_route,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        path = request.url.path
        if path == METRICS_ROUTE:
            return await call_next(request)

        method = request.method
        route = normalize_route(path)
        HTTP_REQUESTS_IN_PROGRESS.labels(method=method, normalized_route=route).inc()
        start = time.perf_counter()
        try:
            response = await call_next(request)
            status = str(response.status_code)
            HTTP_REQUESTS_TOTAL.labels(
                method=method, normalized_route=route, status_code=status
            ).inc()
            if response.status_code >= 400:
                HTTP_ERRORS_TOTAL.labels(normalized_route=route, status_code=status).inc()
            return response
        finally:
            duration = time.perf_counter() - start
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, normalized_route=route).observe(
                duration
            )
            HTTP_REQUESTS_IN_PROGRESS.labels(method=method, normalized_route=route).dec()
