"""Health endpoint tests."""

from fastapi.testclient import TestClient


def test_health_live(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert response.headers.get("X-Request-Id")


def test_health_ready_with_sqlite(client: TestClient) -> None:
    response = client.get("/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["database"] == "up"
