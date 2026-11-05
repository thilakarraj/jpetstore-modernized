"""Checkout idempotency helpers."""

from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel


def checkout_fingerprint(payload: BaseModel) -> str:
    """Stable SHA-256 of canonical checkout JSON (sorted keys)."""
    raw = json.dumps(payload.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
