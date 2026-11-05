"""Alembic migration environment."""

import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from jpetstore.config import (
    ALEMBIC_INI_DEFAULT_URL,
    alembic_ini_sqlalchemy_url,
    database_url_configuration_error,
    migration_url_from_alembic_config,
)
import jpetstore.models  # noqa: F401 — register metadata
from jpetstore.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
_migration_url = migration_url_from_alembic_config(config)
_config_error = database_url_configuration_error(_migration_url)
if _config_error:
    print(f"ERROR: {_config_error}", file=sys.stderr)
    raise SystemExit(2)
_configured = (config.get_main_option("sqlalchemy.url") or "").strip()
if not _configured or _configured == ALEMBIC_INI_DEFAULT_URL:
    config.set_main_option("sqlalchemy.url", alembic_ini_sqlalchemy_url(_migration_url))


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
