"""Phase 3 account, JWT, rate limit, and audit tests."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.orm import Session, sessionmaker

from jpetstore.config import get_settings
from jpetstore.core.rate_limit import get_rate_limiter
from jpetstore.logging_setup import get_security_logger
from jpetstore.models import Account, Signon
from jpetstore.modules.account.schemas import RegisterRequest
from jpetstore.modules.account.service import AccountService
from jpetstore.security.passwords import verify_password

REGISTER_JSON = {
    "username": "newuser",
    "password": "SecretPass1",
    "email": "new@example.com",
    "first_name": "New",
    "last_name": "User",
    "address1": "1 Main St",
    "address2": None,
    "city": "City",
    "state": "ST",
    "zip": "12345",
    "country": "USA",
    "phone": "555-0100",
    "language_preference": "english",
    "favourite_category_id": "DOGS",
    "list_option": True,
    "banner_option": True,
}


def _register(client: TestClient, username: str = "newuser", password: str = "SecretPass1") -> None:
    body = {**REGISTER_JSON, "username": username, "password": password}
    response = client.post("/api/v1/auth/register", json=body)
    assert response.status_code == 201, response.text


def _login(client: TestClient, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def security_audit_records():
    logger = get_security_logger()
    records: list[logging.LogRecord] = []

    class CaptureHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    handler = CaptureHandler()
    logger.addHandler(handler)
    yield records
    logger.removeHandler(handler)


def test_register_success(api_client: TestClient) -> None:
    response = api_client.post("/api/v1/auth/register", json=REGISTER_JSON)
    assert response.status_code == 201
    assert response.json() == {"username": "newuser"}
    assert "password" not in response.text.lower() or "username" in response.json()


def test_register_duplicate_username(api_client: TestClient) -> None:
    _register(api_client)
    response = api_client.post("/api/v1/auth/register", json=REGISTER_JSON)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "USERNAME_EXISTS"


def test_register_invalid_extra_field(api_client: TestClient) -> None:
    body = {**REGISTER_JSON, "userid": "evil"}
    response = api_client.post("/api/v1/auth/register", json=body)
    assert response.status_code == 422


def test_register_password_stored_as_bcrypt(api_client: TestClient, db_engine) -> None:
    _register(api_client, username="hashuser")
    with sessionmaker(bind=db_engine, future=True)() as session:
        signon = session.get(Signon, "hashuser")
        assert signon is not None
        assert signon.password.startswith("$2")
        assert verify_password("SecretPass1", signon.password)


def test_register_transaction_rollback(db_session: Session, monkeypatch) -> None:
    service = AccountService(db_session)
    original_add = db_session.add

    def add_with_signon_failure(obj) -> None:
        if isinstance(obj, Signon):
            raise RuntimeError("signon insert failed")
        original_add(obj)

    monkeypatch.setattr(db_session, "add", add_with_signon_failure)
    payload = RegisterRequest(**{**REGISTER_JSON, "username": "rollback"})
    with pytest.raises(RuntimeError):
        service.register(payload)
    db_session.rollback()
    assert db_session.get(Account, "rollback") is None


def test_login_success(api_client: TestClient) -> None:
    _register(api_client, username="loginuser")
    response = api_client.post(
        "/api/v1/auth/login",
        json={"username": "loginuser", "password": "SecretPass1"},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["expires_in"] == get_settings().jwt_expire_minutes * 60


def test_login_wrong_password(api_client: TestClient) -> None:
    _register(api_client, username="badpass")
    response = api_client.post(
        "/api/v1/auth/login",
        json={"username": "badpass", "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_unknown_user(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/v1/auth/login",
        json={"username": "nobody", "password": "SecretPass1"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid username or password. Signon failed."


def test_jwt_valid_access(api_client: TestClient) -> None:
    _register(api_client, username="jwtuser")
    token = _login(api_client, "jwtuser", "SecretPass1")
    response = api_client.get(
        "/api/v1/account/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "jwtuser"


def test_jwt_expired(api_client: TestClient) -> None:
    settings = get_settings()
    past = datetime.now(tz=UTC) - timedelta(hours=2)
    payload = {
        "sub": "jwtuser",
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": int(past.timestamp()),
        "exp": int((past + timedelta(minutes=5)).timestamp()),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    response = api_client.get(
        "/api/v1/account/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_jwt_invalid_signature(api_client: TestClient) -> None:
    settings = get_settings()
    future = datetime.now(tz=UTC) + timedelta(hours=1)
    payload = {
        "sub": "jwtuser",
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": int(datetime.now(tz=UTC).timestamp()),
        "exp": int(future.timestamp()),
    }
    token = jwt.encode(payload, "wrong-secret-key-at-least-32-chars-long", algorithm="HS256")
    response = api_client.get(
        "/api/v1/account/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_jwt_malformed(api_client: TestClient) -> None:
    response = api_client.get(
        "/api/v1/account/me",
        headers={"Authorization": "Bearer not-a-valid-jwt"},
    )
    assert response.status_code == 401


def test_missing_authorization(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/account/me")
    assert response.status_code == 401


def test_invalid_authorization_scheme(api_client: TestClient) -> None:
    response = api_client.get(
        "/api/v1/account/me",
        headers={"Authorization": "Basic abc"},
    )
    assert response.status_code == 401


def test_get_own_profile(api_client: TestClient) -> None:
    _register(api_client, username="profile1")
    token = _login(api_client, "profile1", "SecretPass1")
    response = api_client.get(
        "/api/v1/account/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["favourite_category_id"] == "DOGS"
    assert "password" not in data


def test_update_own_profile(api_client: TestClient) -> None:
    _register(api_client, username="update1")
    token = _login(api_client, "update1", "SecretPass1")
    response = api_client.put(
        "/api/v1/account/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"city": "New City", "language_preference": "japanese"},
    )
    assert response.status_code == 200
    assert response.json()["city"] == "New City"
    assert response.json()["language_preference"] == "japanese"


def test_cannot_access_other_account_via_token(api_client: TestClient) -> None:
    _register(api_client, username="usera")
    _register(api_client, username="userb")
    token_a = _login(api_client, "usera", "SecretPass1")
    response = api_client.get(
        "/api/v1/account/me",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert response.json()["username"] == "usera"


def test_update_rejects_protected_fields(api_client: TestClient) -> None:
    _register(api_client, username="protected1")
    token = _login(api_client, "protected1", "SecretPass1")
    response = api_client.put(
        "/api/v1/account/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "hacker"},
    )
    assert response.status_code == 422


def test_unauthenticated_update_rejected(api_client: TestClient) -> None:
    response = api_client.put("/api/v1/account/me", json={"city": "X"})
    assert response.status_code == 401


def test_login_rate_limit(api_client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_LOGIN_PER_MINUTE", "2")
    get_settings.cache_clear()
    get_rate_limiter().reset()
    _register(api_client, username="rluser")
    for _ in range(2):
        api_client.post(
            "/api/v1/auth/login",
            json={"username": "rluser", "password": "wrong"},
        )
    response = api_client.post(
        "/api/v1/auth/login",
        json={"username": "rluser", "password": "wrong"},
    )
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"


def test_register_rate_limit(api_client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_REGISTER_PER_MINUTE", "1")
    get_settings.cache_clear()
    get_rate_limiter().reset()
    first = api_client.post("/api/v1/auth/register", json={**REGISTER_JSON, "username": "r1"})
    assert first.status_code == 201
    second = api_client.post("/api/v1/auth/register", json={**REGISTER_JSON, "username": "r2"})
    assert second.status_code == 429


def test_audit_login_success(
    api_client: TestClient, security_audit_records: list[logging.LogRecord]
) -> None:
    _register(api_client, username="auditlogin")
    security_audit_records.clear()
    api_client.post(
        "/api/v1/auth/login",
        json={"username": "auditlogin", "password": "SecretPass1"},
    )
    events = [getattr(r, "event", None) for r in security_audit_records]
    assert "auth.login" in events


def test_audit_login_failure(
    api_client: TestClient, security_audit_records: list[logging.LogRecord]
) -> None:
    _register(api_client, username="auditfail")
    security_audit_records.clear()
    api_client.post(
        "/api/v1/auth/login",
        json={"username": "auditfail", "password": "bad"},
    )
    record = next(r for r in security_audit_records if getattr(r, "event", None) == "auth.login")
    assert getattr(record, "outcome", None) == "failure"


def test_audit_register_success(
    api_client: TestClient, security_audit_records: list[logging.LogRecord]
) -> None:
    security_audit_records.clear()
    api_client.post("/api/v1/auth/register", json={**REGISTER_JSON, "username": "auditreg"})
    record = next(r for r in security_audit_records if getattr(r, "event", None) == "auth.register")
    assert getattr(record, "outcome", None) == "success"


def test_audit_unauthorized_access(
    api_client: TestClient, security_audit_records: list[logging.LogRecord]
) -> None:
    security_audit_records.clear()
    api_client.get("/api/v1/account/me")
    record = next(r for r in security_audit_records if getattr(r, "event", None) == "auth.token")
    assert getattr(record, "outcome", None) == "failure"


def test_audit_register_failure_duplicate(
    api_client: TestClient, security_audit_records: list[logging.LogRecord]
) -> None:
    _register(api_client, username="dupaudit")
    security_audit_records.clear()
    api_client.post("/api/v1/auth/register", json={**REGISTER_JSON, "username": "dupaudit"})
    record = next(r for r in security_audit_records if getattr(r, "event", None) == "auth.register")
    assert getattr(record, "outcome", None) == "failure"


def test_audit_logs_exclude_secrets(
    api_client: TestClient, security_audit_records: list[logging.LogRecord]
) -> None:
    secret = "SuperSecret99"
    security_audit_records.clear()
    api_client.post(
        "/api/v1/auth/register",
        json={**REGISTER_JSON, "username": "secreg", "password": secret},
    )
    blob = json.dumps(
        {
            "messages": [r.getMessage() for r in security_audit_records],
            "extras": [r.__dict__ for r in security_audit_records],
        },
        default=str,
    )
    assert secret not in blob
    assert "SuperSecret" not in blob
