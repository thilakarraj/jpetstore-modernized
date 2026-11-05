"""In-process sliding-window rate limiter (no Redis).

Limitations (ADR-P3-001):
- State is per process; multiple workers/replicas each enforce separate counters.
- Restarts clear counters.
- Client identity uses remote IP only (shared NAT may aggregate clients).
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque


class InMemoryRateLimiter:
    """Thread-safe fixed-window counter per key."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._windows: dict[str, tuple[int, int]] = {}

    def reset(self) -> None:
        with self._lock:
            self._windows.clear()

    def allow(self, key: str, *, limit: int, window_seconds: int = 60) -> bool:
        if limit <= 0:
            return True
        now = int(time.time())
        window_start = now - (now % window_seconds)
        with self._lock:
            prev_start, count = self._windows.get(key, (window_start, 0))
            if prev_start != window_start:
                self._windows[key] = (window_start, 1)
                return True
            if count >= limit:
                return False
            self._windows[key] = (window_start, count + 1)
            return True


_limiter = InMemoryRateLimiter()


def get_rate_limiter() -> InMemoryRateLimiter:
    return _limiter
