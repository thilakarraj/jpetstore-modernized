"""Banner HTML safety helpers."""

from __future__ import annotations

import re

_SCRIPT_TAG = re.compile(r"(?is)<script\b[^>]*>.*?</script>")
_EVENT_HANDLER = re.compile(r"(?i)\s(on\w+)\s*=")


def sanitize_banner_html(raw: str | None) -> str | None:
    """Return legacy banner markup with script blocks and inline handlers removed."""
    if raw is None:
        return None
    cleaned = _SCRIPT_TAG.sub("", raw)
    cleaned = _EVENT_HANDLER.sub(" data-blocked-\\1=", cleaned)
    return cleaned
