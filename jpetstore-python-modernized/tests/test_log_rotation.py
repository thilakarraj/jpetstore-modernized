"""Log rotation configuration tests."""

import logging.handlers
from pathlib import Path

from jpetstore.config import Settings
from jpetstore.logging_setup import configure_logging, shutdown_logging


def test_rotation_policy_uses_retention_days(tmp_path: Path) -> None:
    shutdown_logging()
    settings = Settings(
        jwt_secret="test-jwt-secret-key-with-at-least-32-characters",
        log_dir=str(tmp_path),
        log_retention_days=30,
        log_rotation="midnight",
    )
    configure_logging(settings, enable_stdout=False)
    root = logging.getLogger("jpetstore")
    rotating_handlers = [
        handler
        for handler in root.handlers
        if isinstance(handler, logging.handlers.TimedRotatingFileHandler)
    ]
    assert rotating_handlers
    for handler in rotating_handlers:
        assert handler.when == "MIDNIGHT"
        assert handler.utc is True
        assert handler.backupCount == 30
        assert handler.encoding == "utf-8"
    shutdown_logging()
