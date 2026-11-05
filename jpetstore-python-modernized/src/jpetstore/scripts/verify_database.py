"""Verify MySQL connectivity, migrations, and seed idempotency.

Usage (development database — connection ping only):
  set DATABASE_URL=mysql+pymysql://jpetstore_app:...@host:3306/jpetstore?charset=utf8mb4
  python -m jpetstore.scripts.verify_database

Integration test database (migrate + seed idempotency on jpetstore_test only):
  set TEST_DATABASE_URL=mysql+pymysql://jpetstore_app:...@host:3306/jpetstore_test?charset=utf8mb4
  python -m jpetstore.scripts.verify_database --integration
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from jpetstore.config import (
    Settings,
    alembic_ini_sqlalchemy_url,
    database_name_from_url,
    database_url_configuration_error,
    get_settings,
    integration_database_url_error,
    redact_database_url,
    resolve_test_database_url,
)
from jpetstore.core.database import init_database, session_scope
from jpetstore.logging_setup import configure_logging, get_logger
from jpetstore.seed.runner import count_categories, seed_development_data


def _ping(url: str) -> None:
    engine = create_engine(url, pool_pre_ping=True, future=True)
    with engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1
    engine.dispose()


def _alembic_upgrade(url: str) -> None:
    cfg = Config(str(Path(__file__).resolve().parents[3] / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", alembic_ini_sqlalchemy_url(url))
    command.upgrade(cfg, "head")
    command.current(cfg)
    engine = create_engine(url, future=True)
    tables = set(inspect(engine).get_table_names())
    engine.dispose()
    if "checkout_idempotency" not in tables:
        raise RuntimeError("Phase 6 table checkout_idempotency missing after upgrade")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify database connectivity and migrations")
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Use TEST_DATABASE_URL (jpetstore_test) and run migrate + seed checks",
    )
    args = parser.parse_args()

    if args.integration:
        url = resolve_test_database_url()
        integration_error = integration_database_url_error(url)
        if integration_error:
            print(integration_error, file=sys.stderr)
            return 2
        os.environ["DATABASE_URL"] = url
        os.environ.setdefault("APP_ENV", "test")
        os.environ.setdefault("JWT_SECRET", "test-jwt-secret-key-with-at-least-32-characters")
        get_settings.cache_clear()
    else:
        url = get_settings().database_url
        if database_name_from_url(url) == "jpetstore_test":
            print("Use --integration for jpetstore_test", file=sys.stderr)
            return 2

    config_error = database_url_configuration_error(url)
    if config_error:
        print(f"ERROR: {config_error}", file=sys.stderr)
        return 2

    configure_logging(get_settings())
    logger = get_logger("verify_database")
    logger.info(
        "Checking connectivity",
        extra={"event": "verify.ping", "database": database_name_from_url(url)},
    )
    _ping(url)
    print(f"OK: connection to {database_name_from_url(url)}")

    if args.integration:
        logger.info("Running alembic upgrade head", extra={"event": "verify.migrate"})
        try:
            _alembic_upgrade(url)
        except Exception as exc:
            safe_url = redact_database_url(url)
            print(
                f"ERROR: alembic upgrade failed for {safe_url}: {exc}",
                file=sys.stderr,
            )
            return 1
        print("OK: alembic upgrade head (Phases 1–6)")

        settings = Settings(
            jwt_secret=get_settings().jwt_secret,
            app_env="test",
            database_url=url,
        )
        init_database(settings)
        with session_scope() as session:
            seed_development_data(session, settings)
            first = count_categories(session)
        with session_scope() as session:
            seed_development_data(session, settings)
            second = count_categories(session)
        if first != second:
            print("FAIL: seed not idempotent", file=sys.stderr)
            return 1
        print(f"OK: seed idempotent (categories={first})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
