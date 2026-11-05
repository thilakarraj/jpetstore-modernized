"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Must be set before importing jpetstore modules that load settings.
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault(
    "JWT_SECRET",
    "test-jwt-secret-key-with-at-least-32-characters",
)
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("LOG_DIR", "./logs/test")
os.environ.setdefault("LOG_JSON", "true")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:8000")

from jpetstore.config import get_settings  # noqa: E402
from jpetstore.main import create_app  # noqa: E402
from jpetstore.models import Base  # noqa: E402


@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    @event.listens_for(engine, "connect")
    def _sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection, future=True)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def _reset_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def api_client(db_engine, monkeypatch) -> Generator[TestClient, None, None]:
    """FastAPI client backed by isolated in-memory SQLite with full schema."""
    from jpetstore.core import database as db_module
    from jpetstore.core.rate_limit import get_rate_limiter

    session_factory = sessionmaker(
        bind=db_engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )
    monkeypatch.setattr(db_module, "_engine", db_engine)
    monkeypatch.setattr(db_module, "_SessionLocal", session_factory)
    get_rate_limiter().reset()

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

    get_rate_limiter().reset()


@pytest.fixture(scope="session")
def jpetstore_test_database_url() -> str:
    from mysql_helpers import require_test_database_url

    return require_test_database_url()


@pytest.fixture(scope="session")
def jpetstore_test_schema_ready(jpetstore_test_database_url: str) -> str:
    """Alembic head on jpetstore_test (shared by @mysql tests)."""
    from mysql_helpers import ensure_jpetstore_test_schema

    ensure_jpetstore_test_schema(jpetstore_test_database_url)
    return jpetstore_test_database_url
