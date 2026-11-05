"""SQLAlchemy engine and session factory."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from jpetstore.config import Settings
from jpetstore.logging_setup import get_logger

logger = get_logger("database")

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def init_database(settings: Settings) -> None:
    global _engine, _SessionLocal
    if _engine is not None:
        return
    connect_args: dict[str, object] = {}
    pool_kwargs: dict[str, object] = {}
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if ":memory:" in settings.database_url:
            from sqlalchemy.pool import StaticPool

            pool_kwargs["poolclass"] = StaticPool
    _engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=3600,
        future=True,
        connect_args=connect_args,
        **pool_kwargs,
    )
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)


def get_engine() -> Engine:
    if _engine is None:
        raise RuntimeError("Database not initialized")
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized")
    return _SessionLocal


def check_database_connection() -> bool:
    try:
        engine = get_engine()
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.exception("Database connection check failed")
        return False


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def dispose_database() -> None:
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None
