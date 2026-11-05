"""Prometheus metrics tests."""

from fastapi.testclient import TestClient

from jpetstore.metrics.prometheus import (
    AUTH_LOGIN_ATTEMPTS_TOTAL,
    HTTP_REQUESTS_TOTAL,
    normalize_route,
)


def test_normalize_route_replaces_numeric_ids() -> None:
    assert normalize_route("/api/v1/orders/1000") == "/api/v1/orders/{id}"


def test_metrics_endpoint_exposed(client: TestClient) -> None:
    before = HTTP_REQUESTS_TOTAL.labels(
        method="GET", normalized_route="/health", status_code="200"
    )._value.get()  # noqa: SLF001
    health = client.get("/health")
    assert health.status_code == 200
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "http_requests_total" in metrics.text
    after = HTTP_REQUESTS_TOTAL.labels(
        method="GET", normalized_route="/health", status_code="200"
    )._value.get()  # noqa: SLF001
    assert after >= before


def test_auth_metric_labels_low_cardinality() -> None:
    AUTH_LOGIN_ATTEMPTS_TOTAL.labels(outcome="success").inc()
    AUTH_LOGIN_ATTEMPTS_TOTAL.labels(outcome="failure").inc()
    # Metric names exist without username/email labels by design.
    for metric in AUTH_LOGIN_ATTEMPTS_TOTAL.collect()[0].samples:
        assert "username" not in metric.labels
        assert "email" not in metric.labels
