"""Integration ingress: authenticate, enforce limits, persist request, audit every attempt.

Invariants: INV-P8 (key_id lookup + HMAC verify), INV-P9 (auth/active/limit), INV-P10 (audit each
attempt). Returns the rate-limit result so the router can emit ``X-RateLimit-*`` headers.
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.core.errors import forbidden, rate_limited, unauthorized
from app.core.rate_limit import RateLimitResult, rate_limiter
from app.core.security import parse_api_key, verify_secret
from app.db.base import utcnow
from app.models.integration_request import IntegrationRequest
from app.repositories import api_clients as clients_repo
from app.repositories import api_keys as keys_repo
from app.repositories import audit as audit_repo
from app.repositories import integration_requests as requests_repo
from app.schemas.integration import IntegrationRequestIn

logger = logging.getLogger("app.integration")
ACTION = "integration.submit"


def submit_request(
    db: Session,
    raw_key: str | None,
    data: IntegrationRequestIn,
    *,
    ip_address: str,
    user_agent: str,
) -> tuple[IntegrationRequest, RateLimitResult | None]:
    def audit(client_id: int | None, success: bool, details: dict) -> None:
        audit_repo.create(
            db,
            client_id=client_id,
            action=ACTION,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details,
        )

    # 1) Authenticate by key_id + HMAC secret (FR-I5, FR-I6, INV-P8).
    parsed = parse_api_key(raw_key)
    if parsed is None:
        audit(None, False, {"error": "UNAUTHORIZED", "reason": "missing or malformed api key"})
        raise unauthorized("API key is missing or malformed")
    key_id, secret = parsed
    key = keys_repo.get_by_key_id(db, key_id)
    if key is None or not key.is_active or not verify_secret(secret, key.secret_hash):
        audit(None, False, {"error": "UNAUTHORIZED", "reason": "invalid api key"})
        raise unauthorized("API key is invalid")
    if key.expires_at is not None and key.expires_at < utcnow():
        audit(key.client_id, False, {"error": "UNAUTHORIZED", "reason": "expired api key"})
        raise unauthorized("API key has expired")

    # 2) Active client (FR-I7).
    client = clients_repo.get(db, key.client_id)
    if client is None or not client.is_active:
        audit(key.client_id, False, {"error": "FORBIDDEN", "reason": "client deactivated"})
        raise forbidden("API client is deactivated")

    # 3) Rate limit (FR-I8).
    result = rate_limiter.check(client.id, client.requests_limit_per_minute)
    if not result.allowed:
        audit(client.id, False, {"error": "RATE_LIMIT_EXCEEDED"})
        raise _rate_limit_error(result)

    # 4) Persist accepted request (FR-I10) + success audit (FR-I11/I12); touch key usage.
    key.last_used_at = utcnow()
    keys_repo.save(db, key)
    request = requests_repo.create(
        db,
        client_id=client.id,
        request_type=data.request_type,
        payload=data.payload,
        status="accepted",
    )
    audit(client.id, True, {"request_id": request.id, "request_type": data.request_type})
    logger.info("integration request accepted id=%s client=%s", request.id, client.id)
    return request, result


def _rate_limit_error(result: RateLimitResult):
    err = rate_limited("Per-minute request limit exceeded")
    err.details = {"retry_after": result.reset_after, "limit": result.limit}
    return err


def list_requests(db: Session, **filters) -> tuple[list[IntegrationRequest], int]:
    return requests_repo.list_requests(db, **filters)


__all__ = ["submit_request", "list_requests"]
