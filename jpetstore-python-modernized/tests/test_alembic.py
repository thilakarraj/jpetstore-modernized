"""Alembic migration tests on isolated SQLite database."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, create_engine

from jpetstore.config import get_settings


@pytest.fixture
def alembic_cfg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Config:
    db_file = tmp_path / "alembic_test.db"
    url = f"sqlite+pysqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret-key-with-at-least-32-characters")
    get_settings.cache_clear()
    cfg = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


def test_alembic_upgrade_head(alembic_cfg: Config) -> None:
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(alembic_cfg.get_main_option("sqlalchemy.url"))
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    assert "category" in tables
    assert "orders" in tables
    assert "cart" in tables
    assert "cart_item" in tables
    assert "checkout_idempotency" in tables
    engine.dispose()


def test_alembic_downgrade_to_baseline(alembic_cfg: Config) -> None:
    command.upgrade(alembic_cfg, "head")
    command.downgrade(alembic_cfg, "0001_phase1_baseline")
    engine = create_engine(alembic_cfg.get_main_option("sqlalchemy.url"))
    inspector = inspect(engine)
    assert "category" not in inspector.get_table_names()
    engine.dispose()
