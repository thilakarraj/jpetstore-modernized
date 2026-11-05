"""MySQL integration test helpers — never target the development `jpetstore` database."""

from __future__ import annotations

import os
import threading
from pathlib import Path
from urllib.parse import urlparse

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from jpetstore.config import (
    MYSQL_SEED_REQUIRED_TABLES,
    alembic_ini_sqlalchemy_url,
    database_name_from_url,
)

_mysql_schema_lock = threading.Lock()


def require_test_database_url() -> str:
    url = os.environ.get("TEST_DATABASE_URL", "").strip()
    if not url:
        pytest.skip("TEST_DATABASE_URL is not set — MySQL integration tests skipped")
    parsed = urlparse(url.replace("+pymysql", ""))
    db_name = (parsed.path or "").lstrip("/").split("?")[0]
    if db_name != "jpetstore_test":
        pytest.skip(
            "TEST_DATABASE_URL must use database name jpetstore_test "
            f"(got {db_name!r}) — refusing to run integration tests"
        )
    if db_name == "jpetstore":
        pytest.fail("Refusing to run destructive integration tests against database jpetstore")
    return url


def alembic_upgrade_test_database(url: str) -> None:
    """Run Alembic to head on ``jpetstore_test`` and assert seed prerequisites exist."""
    db_name = database_name_from_url(url)
    if db_name == "jpetstore":
        raise RuntimeError("Refusing to run Alembic test setup against database jpetstore")
    if db_name != "jpetstore_test":
        raise RuntimeError(
            f"TEST_DATABASE_URL must target database jpetstore_test (got {db_name!r})"
        )

    project_root = Path(__file__).resolve().parents[1]
    cfg = Config(str(project_root / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", alembic_ini_sqlalchemy_url(url))
    command.upgrade(cfg, "head")

    engine = create_engine(url, pool_pre_ping=True, future=True)
    try:
        tables = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()

    missing = [name for name in MYSQL_SEED_REQUIRED_TABLES if name not in tables]
    if missing:
        raise RuntimeError(
            "MySQL test schema incomplete after Alembic upgrade on jpetstore_test; "
            f"missing tables: {', '.join(missing)}"
        )


def ensure_jpetstore_test_schema(url: str) -> None:
    """Thread-safe Alembic upgrade + table checks for shared MySQL test fixtures."""
    with _mysql_schema_lock:
        alembic_upgrade_test_database(url)
