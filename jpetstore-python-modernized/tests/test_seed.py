"""Seed idempotency tests."""

from jpetstore.config import Settings
from jpetstore.seed.legacy_data import CATEGORIES
from jpetstore.seed.runner import count_categories, seed_development_data


def test_seed_is_idempotent(db_session) -> None:
    settings = Settings(
        jwt_secret="test-jwt-secret-key-with-at-least-32-characters",
        app_env="development",
    )
    seed_development_data(db_session, settings)
    assert count_categories(db_session) == len(CATEGORIES)
    seed_development_data(db_session, settings)
    assert count_categories(db_session) == len(CATEGORIES)


def test_seed_refuses_production(db_session) -> None:
    settings = Settings(
        jwt_secret="test-jwt-secret-key-with-at-least-32-characters",
        app_env="production",
    )
    import pytest

    with pytest.raises(RuntimeError, match="production"):
        seed_development_data(db_session, settings)
