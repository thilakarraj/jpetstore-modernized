"""Prometheus metric definitions."""

from prometheus_client import Counter, Gauge, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "normalized_route", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "normalized_route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "In-flight HTTP requests",
    ["method", "normalized_route"],
)

HTTP_ERRORS_TOTAL = Counter(
    "http_errors_total",
    "HTTP responses with status >= 400",
    ["normalized_route", "status_code"],
)

AUTH_LOGIN_ATTEMPTS_TOTAL = Counter(
    "auth_login_attempts_total",
    "Login attempts",
    ["outcome"],
)

AUTH_REGISTRATION_TOTAL = Counter(
    "auth_registration_total",
    "Registration attempts",
    ["outcome"],
)

CART_ADD_TOTAL = Counter(
    "cart_add_total",
    "Cart item add attempts",
    ["outcome"],
)

CART_UPDATE_TOTAL = Counter(
    "cart_update_total",
    "Cart item update attempts",
    ["outcome"],
)

CART_REMOVE_TOTAL = Counter(
    "cart_remove_total",
    "Cart item remove or clear attempts",
    ["outcome"],
)

ORDERS_CREATED_TOTAL = Counter(
    "orders_created_total",
    "Orders created",
    ["outcome"],
)

DATABASE_QUERY_DURATION_SECONDS = Histogram(
    "database_query_duration_seconds",
    "Database operation duration",
    ["operation", "outcome"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0),
)

METRICS_ROUTE = "/metrics"
HEALTH_ROUTE = "/health"
READY_ROUTE = "/health/ready"


def normalize_route(path: str) -> str:
    """Collapse dynamic segments to keep label cardinality low."""
    if path == METRICS_ROUTE:
        return METRICS_ROUTE
    if path.startswith("/api/v1/"):
        parts = path.split("/")
        normalized: list[str] = []
        for index, part in enumerate(parts):
            if index >= 4 and part and not part.startswith("{"):
                if part.isdigit():
                    normalized.append("{id}")
                    continue
                if len(part) <= 20 and part.isalnum():
                    normalized.append(part)
                    continue
                normalized.append("{param}")
            else:
                normalized.append(part)
        return "/".join(normalized)
    return path
