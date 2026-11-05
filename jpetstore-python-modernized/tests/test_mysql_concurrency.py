"""MySQL checkout concurrency tests (MySQL 8 + TEST_DATABASE_URL only)."""

from __future__ import annotations

import threading

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jpetstore.modules.order.repository import OrderRepository
from seed_helpers import ensure_catalog_seeded

pytestmark = pytest.mark.mysql


@pytest.fixture(scope="module")
def mysql_session_factory(jpetstore_test_schema_ready: str):
    url = jpetstore_test_schema_ready
    engine = create_engine(url, pool_pre_ping=True, future=True)
    with sessionmaker(bind=engine, future=True)() as session:
        ensure_catalog_seeded(session)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    yield factory
    engine.dispose()


def test_concurrent_sequence_allocation(mysql_session_factory) -> None:
    """Two threads each allocate an order id; IDs must differ (MySQL row lock on sequence)."""
    barrier = threading.Barrier(2)
    results: list[int] = []
    errors: list[Exception] = []

    def worker() -> None:
        session = mysql_session_factory()
        try:
            barrier.wait(timeout=10)
            repo = OrderRepository(session)
            seq = repo.lock_sequence("ordernum")
            order_id = seq.nextid
            seq.nextid = order_id + 1
            session.commit()
            results.append(order_id)
        except Exception as exc:
            errors.append(exc)
        finally:
            session.close()

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start()
    t2.start()
    t1.join(timeout=30)
    t2.join(timeout=30)
    assert not errors, errors
    assert len(results) == 2
    assert results[0] != results[1]
