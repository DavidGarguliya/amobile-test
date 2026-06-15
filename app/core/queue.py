"""Task queue abstraction for integration processing (brief §48).

Default ``InlineTaskQueue`` runs jobs synchronously in-process (used by the admin-triggered
``/process`` endpoint, keeping its response synchronous). ``ArqTaskQueue`` enqueues to Redis for a
background worker (see ``app/worker.py``) with retries + dead-letter handling. Backend is selected by
``REDIS_URL``.
"""

from __future__ import annotations

import logging
from typing import Any, Protocol

from app.core.config import settings
from app.db.session import SessionLocal
from app.services import processing

logger = logging.getLogger("app.queue")


def run_process_job(request_id: int) -> str:
    """Job body: process one integration request. Used inline and by the Arq worker."""
    db = SessionLocal()
    try:
        _, message = processing.process_request(db, request_id)
        return message
    finally:
        db.close()


class TaskQueue(Protocol):
    def enqueue_process(self, request_id: int) -> Any: ...


class InlineTaskQueue:
    """Synchronous in-process execution (default)."""

    def enqueue_process(self, request_id: int) -> str:
        return run_process_job(request_id)


class ArqTaskQueue:  # pragma: no cover - exercised only when Redis/arq are configured
    """Enqueue to Redis via arq for background processing."""

    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url

    def enqueue_process(self, request_id: int) -> None:
        import asyncio

        from arq import create_pool
        from arq.connections import RedisSettings

        async def _enqueue() -> None:
            pool = await create_pool(RedisSettings.from_dsn(self._redis_url))
            await pool.enqueue_job("process_integration_request", request_id)

        asyncio.run(_enqueue())


def _build_queue() -> TaskQueue:
    if settings.redis_url:
        try:  # pragma: no cover
            import arq  # noqa: F401

            return ArqTaskQueue(settings.redis_url)
        except Exception:
            pass
    return InlineTaskQueue()


task_queue: TaskQueue = _build_queue()
