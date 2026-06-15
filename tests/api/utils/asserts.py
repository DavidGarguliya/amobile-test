"""Custom assertions. Assertions live in tests/helpers, never inside POM client objects."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ValidationError

from tests.api.clients.base_client import ApiResponse
from tests.api.schemas.common import ERROR_CODES, ErrorEnvelope, extract_items, extract_total


def assert_status(response: ApiResponse, *allowed: int) -> None:
    assert response.status_code in allowed, (
        f"expected status in {allowed}, got {response.status_code}; body={response.json or response.text!r}"
    )


def assert_not_success(response: ApiResponse) -> None:
    """For ambiguous error codes the brief does not pin down (Q-7): require a 4xx/5xx, not a 2xx."""
    assert not response.ok, (
        f"expected a non-2xx error response, got {response.status_code}; body={response.json or response.text!r}"
    )


def assert_error_envelope(response: ApiResponse, *expected_codes: str) -> ErrorEnvelope:
    """Validate the unified error envelope (INV-X1) and that ``code`` is in the allowed set (INV-X2)."""
    assert_not_success(response)
    body = response.json
    assert isinstance(body, dict), f"error body must be a JSON object, got {type(body)!r}: {response.text!r}"
    try:
        envelope = ErrorEnvelope.model_validate(body)
    except ValidationError as exc:  # pragma: no cover - assertion path
        raise AssertionError(f"error body does not match the unified envelope: {exc}") from exc
    assert envelope.error is True, f"error envelope must have error=true, got {envelope.error!r}"
    assert envelope.code in ERROR_CODES, f"unknown error code {envelope.code!r}; allowed={sorted(ERROR_CODES)}"
    if expected_codes:
        assert envelope.code in expected_codes, (
            f"expected error code in {expected_codes}, got {envelope.code!r}"
        )
    return envelope


def assert_schema(data: Any, model: type[BaseModel]) -> BaseModel:
    """Validate a response body (or item) against a pydantic contract schema."""
    try:
        return model.model_validate(data)
    except ValidationError as exc:  # pragma: no cover - assertion path
        raise AssertionError(f"response does not match {model.__name__} contract: {exc}") from exc


def assert_pagination(body: Any, limit: int) -> list[Any]:
    """Assert the response is paginated: items list present and bounded by ``limit``."""
    items = extract_items(body)
    assert len(items) <= limit, f"page returned {len(items)} items, exceeds limit={limit}"
    total = extract_total(body)
    if total is not None:
        assert total >= len(items), f"total={total} is smaller than returned items={len(items)}"
    return items
