"""In-memory per-client rate limiter (ADR-004, FR-I8, INV-P9).

Fixed window of one minute keyed by (client_id, minute-bucket). This is process-local and therefore
not consistent across multiple instances — production would move this to Redis (brief §49). The
implementation is explicit and deterministic given a clock (no hidden state beyond the counter map).
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict


class RateLimiter:
    def __init__(self, clock=time.time) -> None:
        self._clock = clock
        self._lock = threading.Lock()
        self._counters: dict[tuple[int, int], int] = defaultdict(int)

    def allow(self, client_id: int, limit_per_minute: int) -> bool:
        """Register one hit; return True if within ``limit_per_minute``, False if exceeded."""
        if limit_per_minute <= 0:
            return True
        bucket = int(self._clock() // 60)
        key = (client_id, bucket)
        with self._lock:
            self._counters[key] += 1
            current = self._counters[key]
            # opportunistic cleanup of stale buckets to bound memory
            if len(self._counters) > 1024:
                self._counters = defaultdict(int, {k: v for k, v in self._counters.items() if k[1] >= bucket})
        return current <= limit_per_minute


rate_limiter = RateLimiter()
