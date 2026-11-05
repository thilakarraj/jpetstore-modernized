"""Database transaction rollback tests."""

from jpetstore.models import Category


def test_session_rollback_discards_uncommitted(db_session) -> None:
    db_session.add(Category(catid="FISH", name="Fish", descn=None))
    db_session.rollback()
    assert db_session.get(Category, "FISH") is None
