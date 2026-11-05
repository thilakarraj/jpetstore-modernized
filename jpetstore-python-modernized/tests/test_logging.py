"""Logging redaction and configuration tests."""

import json
import logging
from pathlib import Path

from jpetstore.config import Settings
from jpetstore.logging_setup import RedactingFilter, configure_logging, redact_mapping, shutdown_logging


def test_redact_mapping_removes_sensitive_fields() -> None:
    payload = {
        "username": "j2ee",
        "password": "secret",
        "authorization": "Bearer abc.def.ghi",
        "credit_card": "4111111111111111",
    }
    redacted = redact_mapping(payload)
    assert redacted["password"] == "[REDACTED]"
    assert redacted["authorization"] == "[REDACTED]"
    assert redacted["credit_card"] == "[REDACTED]"
    assert redacted["username"] == "j2ee"


def test_redacting_filter_on_log_record() -> None:
    filt = RedactingFilter()
    record = logging.LogRecord(
        name="jpetstore.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="login password=%s token=%s",
        args=("secret", "Bearer token"),
        exc_info=None,
    )
    record.password = "secret"
    record.jwt = "abc"
    assert filt.filter(record) is True
    assert record.password == "[REDACTED]"
    assert record.jwt == "[REDACTED]"


def test_logging_configuration_creates_files(tmp_path: Path) -> None:
    shutdown_logging()
    settings = Settings(
        jwt_secret="test-jwt-secret-key-with-at-least-32-characters",
        log_dir=str(tmp_path),
        log_retention_days=30,
        log_json=True,
    )
    configure_logging(settings, enable_stdout=False, force=True)
    logger = logging.getLogger("jpetstore.testfiles")
    logger.info("application log entry")
    logger.error("error log entry")
    security = logging.getLogger("jpetstore.security")
    security.info("security audit entry")
    for handler in logging.getLogger("jpetstore").handlers:
        handler.flush()
    for handler in logging.getLogger("jpetstore.security").handlers:
        handler.flush()
    shutdown_logging()
    assert (tmp_path / "application.log").exists()
    assert (tmp_path / "error.log").exists()
    assert (tmp_path / "security-audit.log").exists()
    line = (tmp_path / "application.log").read_text(encoding="utf-8").splitlines()[0]
    json.loads(line)
