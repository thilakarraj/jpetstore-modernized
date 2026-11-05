"""Settings tests."""

import pytest

from jpetstore.config import Settings


def test_settings_cors_origins_parsed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    settings = Settings(
        jwt_secret="test-jwt-secret-key-with-at-least-32-characters",
        cors_origins="http://a.example,http://b.example",
    )
    assert settings.cors_origin_list == ["http://a.example", "http://b.example"]
