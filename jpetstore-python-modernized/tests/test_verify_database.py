"""Unit tests for database verification script and URL helpers."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest
from alembic.config import Config

from jpetstore.config import (
    Settings,
    alembic_ini_sqlalchemy_url,
    database_name_from_url,
    get_settings,
    integration_database_url_error,
    redact_database_url,
    resolve_test_database_url,
)
from jpetstore.scripts import verify_database


@pytest.fixture
def jwt_secret() -> str:
    return "test-jwt-secret-key-with-at-least-32-characters"


def test_test_database_url_loaded_from_env_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, jwt_secret: str
) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "TEST_DATABASE_URL=mysql+pymysql://app_user:secr%40et@127.0.0.1:3306/jpetstore_test?charset=utf8mb4\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    get_settings.cache_clear()
    settings = Settings(jwt_secret=jwt_secret, _env_file=str(env_path))
    assert settings.test_database_url.endswith("/jpetstore_test?charset=utf8mb4")
    assert "secr%40et" in settings.test_database_url


def test_test_database_url_process_env_overrides_env_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, jwt_secret: str
) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "TEST_DATABASE_URL=mysql+pymysql://from_env_file@127.0.0.1/jpetstore_test\n",
        encoding="utf-8",
    )
    monkeypatch.setenv(
        "TEST_DATABASE_URL",
        "mysql+pymysql://from_process@127.0.0.1/jpetstore_test?charset=utf8mb4",
    )
    get_settings.cache_clear()
    settings = Settings(jwt_secret=jwt_secret, _env_file=str(env_path))
    assert "from_process" in settings.test_database_url
    assert "from_env_file" not in settings.test_database_url


def test_resolve_test_database_url_uses_settings(
    monkeypatch: pytest.MonkeyPatch, jwt_secret: str
) -> None:
    monkeypatch.setenv(
        "TEST_DATABASE_URL",
        "mysql+pymysql://u:p@127.0.0.1:3306/jpetstore_test?charset=utf8mb4",
    )
    monkeypatch.setenv("JWT_SECRET", jwt_secret)
    get_settings.cache_clear()
    assert resolve_test_database_url().endswith("jpetstore_test?charset=utf8mb4")


def test_integration_rejects_jpetstore_database() -> None:
    url = "mysql+pymysql://u:pass%21@127.0.0.1:3306/jpetstore?charset=utf8mb4"
    err = integration_database_url_error(url)
    assert err is not None
    assert "must not target database jpetstore" in err
    assert "pass" not in err
    assert "%21" not in err


def test_integration_rejects_wrong_database_name() -> None:
    url = "mysql+pymysql://u:p@127.0.0.1:3306/other_db?charset=utf8mb4"
    err = integration_database_url_error(url)
    assert err == "TEST_DATABASE_URL must target database jpetstore_test"


def test_integration_accepts_jpetstore_test() -> None:
    url = "mysql+pymysql://u:pass%21@127.0.0.1:3306/jpetstore_test?charset=utf8mb4"
    assert integration_database_url_error(url) is None


@pytest.mark.parametrize(
    "raw_url",
    [
        "mysql+pymysql://u:pass%21@127.0.0.1:3306/db?charset=utf8mb4",
        "mysql+pymysql://u:p%40ss%23word@127.0.0.1:3306/db?charset=utf8mb4",
    ],
)
def test_alembic_ini_sqlalchemy_url_roundtrip(raw_url: str) -> None:
    cfg = Config()
    cfg.set_main_option("sqlalchemy.url", alembic_ini_sqlalchemy_url(raw_url))
    assert cfg.get_main_option("sqlalchemy.url") == raw_url


def test_redact_database_url_hides_password() -> None:
    url = "mysql+pymysql://jpetstore_app:jpetstore_app%21@127.0.0.1:3306/jpetstore_test?charset=utf8mb4"
    redacted = redact_database_url(url)
    assert "jpetstore_app%21" not in redacted
    assert "jpetstore_app!" not in redacted
    assert "***" in redacted


def test_verify_integration_error_never_includes_password(
    monkeypatch: pytest.MonkeyPatch, jwt_secret: str, capsys: pytest.CaptureFixture[str]
) -> None:
    secret = "super_secret%21value"
    monkeypatch.setenv(
        "TEST_DATABASE_URL",
        f"mysql+pymysql://user:{secret}@127.0.0.1:3306/jpetstore?charset=utf8mb4",
    )
    monkeypatch.setenv("JWT_SECRET", jwt_secret)
    get_settings.cache_clear()
    monkeypatch.setattr(verify_database, "_ping", lambda _url: None)
    monkeypatch.setattr(sys, "argv", ["verify_database", "--integration"])
    exit_code = verify_database.main()
    captured = capsys.readouterr()
    assert exit_code == 2
    assert secret not in captured.err
    assert "super_secret" not in captured.err


def test_verify_integration_happy_path_mocked(
    monkeypatch: pytest.MonkeyPatch, jwt_secret: str, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv(
        "TEST_DATABASE_URL",
        "mysql+pymysql://u:p%21@127.0.0.1:3306/jpetstore_test?charset=utf8mb4",
    )
    monkeypatch.setenv("JWT_SECRET", jwt_secret)
    get_settings.cache_clear()
    monkeypatch.setattr(verify_database, "_ping", lambda _url: None)
    monkeypatch.setattr(verify_database, "_alembic_upgrade", lambda _url: None)
    monkeypatch.setattr(verify_database, "init_database", lambda _settings: None)

    class _Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(verify_database, "session_scope", lambda: _Ctx())
    monkeypatch.setattr(verify_database, "seed_development_data", lambda *_a, **_k: None)
    monkeypatch.setattr(verify_database, "count_categories", lambda _s: 5)
    monkeypatch.setattr(sys, "argv", ["verify_database", "--integration"])
    exit_code = verify_database.main()
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "OK: connection to jpetstore_test" in captured.out
    assert "OK: alembic upgrade head" in captured.out
    assert "OK: seed idempotent" in captured.out
    assert database_name_from_url(get_settings().database_url) != "jpetstore"


def test_verify_logs_do_not_contain_password(
    monkeypatch: pytest.MonkeyPatch,
    jwt_secret: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    raw_password = "log_secret%21"
    monkeypatch.setenv(
        "TEST_DATABASE_URL",
        f"mysql+pymysql://user:{raw_password}@127.0.0.1:3306/jpetstore_test?charset=utf8mb4",
    )
    monkeypatch.setenv("JWT_SECRET", jwt_secret)
    get_settings.cache_clear()
    monkeypatch.setattr(verify_database, "_ping", lambda _url: None)
    monkeypatch.setattr(verify_database, "_alembic_upgrade", lambda _url: None)
    monkeypatch.setattr(verify_database, "init_database", lambda _settings: None)

    class _Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(verify_database, "session_scope", lambda: _Ctx())
    monkeypatch.setattr(verify_database, "seed_development_data", lambda *_a, **_k: None)
    monkeypatch.setattr(verify_database, "count_categories", lambda _s: 1)
    monkeypatch.setattr(sys, "argv", ["verify_database", "--integration"])

    with caplog.at_level(logging.INFO, logger="jpetstore.verify_database"):
        verify_database.main()

    log_text = caplog.text
    assert raw_password not in log_text
    assert "log_secret" not in log_text
