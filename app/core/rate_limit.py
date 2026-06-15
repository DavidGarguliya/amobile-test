"""Rate limiting behind a small interface (ADR-004, FR-I8, INV-P9).

Default backend is in-process (fixed window per minute). A Redis backend is selected automatically
when ``REDIS_URL`` is configured and the ``redis`` package is importable — giving consistent limits
across instances (brief §49). Both are explicit and deterministic given a clock.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Protocol

from app.core.config import settings


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    reset_after: int  # seconds until the window resets


class RateLimiter(Protocol):
    def check(self, client_id: int, limit_per_minute: int) -> RateLimitResult: ...


class InMemoryRateLimiter:
    """Fixed one-minute window keyed by (client_id, minute-bucket). Process-local."""

    def __init__(self, clock=time.time) -> None:
        self._clock = clock
        self._lock = threading.Lock()
        self._counters: dict[tuple[int, int], int] = defaultdict(int)

    def check(self, client_id: int, limit_per_minute: int) -> RateLimitResult:
        if limit_per_minute <= 0:
            return RateLimitResult(True, limit_per_minute, 0, 0)
        now = self._clock()
        bucket = int(now // 60)
        reset_after = 60 - int(now % 60)
        key = (client_id, bucket)
        with self._lock:
            self._counters[key] += 1
            current = self._counters[key]
            if len(self._counters) > 1024:
                self._counters = defaultdict(int, {k: v for k, v in self._counters.items() if k[1] >= bucket})
        remaining = max(0, limit_per_minute - current)
        return RateLimitResult(current <= limit_per_minute, limit_per_minute, remaining, reset_after)


class RedisRateLimiter:
    """Fixed-window limiter backed by Redis (atomic INCR + EXPIRE). Consistent across instances."""

    def __init__(self, client) -> None:
        self._redis = client

    def check(self, client_id: int, limit_per_minute: int) -> RateLimitResult:
        if limit_per_minute <= 0:
            return RateLimitResult(True, limit_per_minute, 0, 0)
        now = int(time.time())
        bucket = now // 60
        reset_after = 60 - (now % 60)
        key = f"rl:{client_id}:{bucket}"
        pipe = self._redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)
        current, _ = pipe.execute()
        remaining = max(0, limit_per_minute - int(current))
        return RateLimitResult(int(current) <= limit_per_minute, limit_per_minute, remaining, reset_after)


def _build_rate_limiter() -> RateLimiter:
    if settings.redis_url:
        try:  # pragma: no cover - exercised only when Redis is configured
            import redis  # type: ignore

            return RedisRateLimiter(redis.Redis.from_url(settings.redis_url))
        except Exception:
            pass
    return InMemoryRateLimiter()


rate_limiter: RateLimiter = _build_rate_limiter()
