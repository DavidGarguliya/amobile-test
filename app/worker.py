"""Arq worker for background integration processing (brief §48, §49).

Run with: ``arq app.worker.WorkerSettings`` (requires REDIS_URL and the ``arq`` package).
Jobs are retried; after ``max_tries`` a job is dead-lettered to the audit log (DLQ).
"""

from __future__ import annotations

import logging

from app.core.config import settings
from app.core.queue import run_process_job
from app.db.session import SessionLocal
from app.repositories import audit as audit_repo

logger = logging.getLogger("app.worker")
MAX_TRIES = 5


async def process_integration_request(ctx: dict, request_id: int) -> str:
    return run_process_job(request_id)


async def _dead_letter(ctx: dict, exc: Exception) -> None:  # pragma: no cover - infra path
    request_id = (ctx.get("job_args") or [None])[0]
    db = SessionLocal()
    try:
        audit_repo.create(
            db,
            client_id=None,
            action="integration.process.dead_letter",
            ip_address="",
            user_agent="worker",
            success=False,
            details={"request_id": request_id, "error": str(exc)},
        )
    finally:
        db.close()
    logger.error("dead-lettered job request_id=%s: %s", request_id, exc)


class WorkerSettings:  # pragma: no cover - infra path
    functions = [process_integration_request]
    max_tries = MAX_TRIES
    on_job_failure = _dead_letter

    @staticmethod
    def redis_settings():
        from arq.connections import RedisSettings

        return RedisSettings.from_dsn(settings.redis_url or "redis://localhost:6379")
