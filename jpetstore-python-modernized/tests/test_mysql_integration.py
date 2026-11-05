"""MySQL 8 integration tests (optional; require TEST_DATABASE_URL).

These tests mutate `jpetstore_test` only. They are skipped when TEST_DATABASE_URL is unset.
Unit tests continue to use in-memory SQLite (see tests/conftest.py).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from jpetstore.config import Settings, alembic_ini_sqlalchemy_url, get_settings
from jpetstore.seed.runner import count_categories, seed_development_data
from mysql_helpers import require_test_database_url

pytestmark = pytest.mark.mysql


@pytest.fixture(scope="module")
def test_database_url(jpetstore_test_schema_ready: str) -> str:
    return jpetstore_test_schema_ready


@pytest.fixture(scope="module")
def mysql_engine(test_database_url: str):
    engine = create_engine(test_database_url, pool_pre_ping=True, future=True)
    yield engine
    engine.dispose()


def test_mysql_connection(mysql_engine) -> None:
    with mysql_engine.connect() as conn:
        row = conn.execute(text("SELECT 1")).scalar()
        assert row == 1


def test_alembic_upgrade_head(test_database_url: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", test_database_url)
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret-key-with-at-least-32-characters")
    get_settings.cache_clear()
    cfg = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", alembic_ini_sqlalchemy_url(test_database_url))
    command.upgrade(cfg, "head")
    engine = create_engine(test_database_url, future=True)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    assert "checkout_idempotency" in tables
    assert "cart" in tables
    assert "orders" in tables
    assert "bannerdata" in tables
    engine.dispose()


def test_seed_idempotent_on_mysql(test_database_url: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", test_database_url)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret-key-with-at-least-32-characters")
    get_settings.cache_clear()
    settings = Settings(
        jwt_secret="test-jwt-secret-key-with-at-least-32-characters",
        app_env="test",
        database_url=test_database_url,
    )
    engine = create_engine(test_database_url, future=True)
    Session = sessionmaker(bind=engine, future=True)
    with Session() as session:
        seed_development_data(session, settings)
        first = count_categories(session)
        seed_development_data(session, settings)
        second = count_categories(session)
    assert first == second == 5
    engine.dispose()
