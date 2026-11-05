"""Structured logging with redaction and rotating file handlers."""

from __future__ import annotations

import gzip
import json
import logging
import logging.handlers
import os
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jpetstore.config import Settings

SENSITIVE_KEYS = frozenset(
    {
        "password",
        "passwd",
        "pwd",
        "secret",
        "token",
        "authorization",
        "cookie",
        "cookies",
        "jwt",
        "access_token",
        "refresh_token",
        "credit_card",
        "creditcard",
        "cvv",
        "cvc",
        "database_url",
        "jwt_secret",
    }
)

REDACTED = "[REDACTED]"

_CONFIGURED = False
_FILE_HANDLERS: list[logging.Handler] = []


class RedactingFilter(logging.Filter):
    """Redact sensitive keys in log record messages and extra dicts."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = self._redact_value(record.msg)
        if isinstance(record.args, dict):
            record.args = {k: self._redact_value(v) for k, v in record.args.items()}
        elif isinstance(record.args, tuple):
            record.args = tuple(self._redact_value(a) for a in record.args)
        for key, value in record.__dict__.items():
            if key in ("msg", "args", "message"):
                continue
            if self._is_sensitive_key(key):
                setattr(record, key, REDACTED)
            elif isinstance(value, (dict, list, tuple, str)):
                setattr(record, key, self._redact_value(value))
        return True

    def _is_sensitive_key(self, key: str) -> bool:
        lowered = key.lower()
        return any(part in lowered for part in SENSITIVE_KEYS)

    def _redact_value(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                k: REDACTED if self._is_sensitive_key(str(k)) else self._redact_value(v)
                for k, v in value.items()
            }
        if isinstance(value, list):
            return [self._redact_value(item) for item in value]
        if isinstance(value, tuple):
            return tuple(self._redact_value(item) for item in value)
        if isinstance(value, str) and "Bearer " in value:
            return REDACTED
        return value


class JsonFormatter(logging.Formatter):
    """JSON log line formatter."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in (
            "request_id",
            "method",
            "route",
            "status_code",
            "duration_ms",
            "event",
            "outcome",
            "client_ip",
            "failure_category",
            "user_identifier",
        ):
            if hasattr(record, field):
                payload[field] = getattr(record, field)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def _gzip_rotator(source: str, dest: str) -> None:
    """Compress rotated log file to .gz and remove uncompressed dest."""
    with open(source, "rb") as src_file:
        with gzip.open(f"{dest}.gz", "wb") as gz_file:
            shutil.copyfileobj(src_file, gz_file)
    os.remove(source)


def _gzip_namer(default_name: str) -> str:
    return default_name


def _build_file_handler(
    log_path: Path,
    settings: Settings,
    level: int,
) -> logging.Handler:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(log_path),
        when=settings.log_rotation,
        interval=1,
        backupCount=settings.log_retention_days,
        encoding="utf-8",
        utc=True,
    )
    handler.rotator = _gzip_rotator  # type: ignore[attr-defined]
    handler.namer = _gzip_namer  # type: ignore[attr-defined]
    handler.setLevel(level)
    if settings.log_json:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
    handler.addFilter(RedactingFilter())
    return handler


def configure_logging(
    settings: Settings,
    *,
    enable_stdout: bool = True,
    force: bool = False,
) -> None:
    """Configure application, error, and security-audit log streams."""
    global _CONFIGURED, _FILE_HANDLERS
    if _CONFIGURED and not force:
        return
    if _CONFIGURED and force:
        shutdown_logging()

    log_dir = Path(settings.log_dir).resolve()
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("jpetstore")
    root.setLevel(settings.log_level)
    root.propagate = False
    root.handlers.clear()

    redacting = RedactingFilter()

    app_handler = _build_file_handler(log_dir / "application.log", settings, logging.INFO)
    error_handler = _build_file_handler(log_dir / "error.log", settings, logging.ERROR)
    security_handler = _build_file_handler(
        log_dir / "security-audit.log", settings, logging.INFO
    )
    _FILE_HANDLERS = [app_handler, error_handler, security_handler]

    root.addHandler(app_handler)
    root.addHandler(error_handler)

    if enable_stdout:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(settings.log_level)
        stream_handler.setFormatter(JsonFormatter() if settings.log_json else logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        ))
        stream_handler.addFilter(redacting)
        root.addHandler(stream_handler)

    security_logger = logging.getLogger("jpetstore.security")
    security_logger.setLevel(logging.INFO)
    security_logger.propagate = False
    security_logger.handlers.clear()
    security_logger.addHandler(security_handler)

    _CONFIGURED = True


def shutdown_logging() -> None:
    """Close and flush file handlers on application shutdown."""
    global _CONFIGURED, _FILE_HANDLERS
    root = logging.getLogger("jpetstore")
    security_logger = logging.getLogger("jpetstore.security")
    for handler in list(root.handlers) + list(security_logger.handlers):
        handler.flush()
        handler.close()
    root.handlers.clear()
    security_logger.handlers.clear()
    _FILE_HANDLERS = []
    _CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"jpetstore.{name}")


def get_security_logger() -> logging.Logger:
    return logging.getLogger("jpetstore.security")


def redact_mapping(data: dict[str, Any]) -> dict[str, Any]:
    """Public helper for tests and explicit audit payloads."""
    filt = RedactingFilter()
    return filt._redact_value(data)  # noqa: SLF001
