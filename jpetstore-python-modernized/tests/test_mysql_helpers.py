"""Regression tests for MySQL test DB setup helpers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from alembic.config import Config

from jpetstore.config import (
    ALEMBIC_INI_DEFAULT_URL,
    alembic_ini_sqlalchemy_url,
    get_settings,
    migration_url_from_alembic_config,
)
from mysql_helpers import alembic_upgrade_test_database


def test_migration_url_from_alembic_config_prefers_set_main_option(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///must-not-use-for-alembic")
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret-key-with-at-least-32-characters")
    get_settings.cache_clear()
    cfg = Config()
    test_url = "mysql+pymysql://user:pass%21@127.0.0.1:3306/jpetstore_test?charset=utf8mb4"
    cfg.set_main_option("sqlalchemy.url", alembic_ini_sqlalchemy_url(test_url))
    assert migration_url_from_alembic_config(cfg) == test_url


def test_migration_url_from_alembic_config_falls_back_to_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///from-settings")
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret-key-with-at-least-32-characters")
    get_settings.cache_clear()
    cfg = Config()
    cfg.set_main_option("sqlalchemy.url", ALEMBIC_INI_DEFAULT_URL)
    assert migration_url_from_alembic_config(cfg) == "sqlite+pysqlite:///from-settings"


def test_alembic_upgrade_test_database_rejects_jpetstore() -> None:
    url = "mysql+pymysql://user:pass@127.0.0.1:3306/jpetstore?charset=utf8mb4"
    with pytest.raises(RuntimeError, match="Refusing to run Alembic test setup against database jpetstore"):
        alembic_upgrade_test_database(url)


@patch("mysql_helpers.command.upgrade")
@patch("mysql_helpers.create_engine")
@patch("mysql_helpers.inspect")
def test_alembic_upgrade_test_database_verifies_bannerdata(
    mock_inspect: MagicMock,
    mock_create_engine: MagicMock,
    mock_upgrade: MagicMock,
) -> None:
    url = "mysql+pymysql://user:pass%21@127.0.0.1:3306/jpetstore_test?charset=utf8mb4"
    engine = MagicMock()
    mock_create_engine.return_value = engine
    mock_inspect.return_value.get_table_names.return_value = ["category", "supplier"]

    with pytest.raises(RuntimeError, match="bannerdata"):
        alembic_upgrade_test_database(url)

    mock_upgrade.assert_called_once()
    cfg_arg = mock_upgrade.call_args[0][0]
    assert cfg_arg.get_main_option("sqlalchemy.url") == url
