"""Shared response schemas: the unified error envelope and pagination helpers.

Contract checks validate both the HTTP status code and the response body shape (TEST_PLAN §1).
Models use ``extra="ignore"`` so they assert the presence/типы of known fields without failing on
additional fields a real implementation may add.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

# Allowed error codes — brief §5.3 / NFR-3 / invariant INV-X2.
ERROR_CODES: frozenset[str] = frozenset(
    {
        "VALIDATION_ERROR",
        "NOT_FOUND",
        "UNAUTHORIZED",
        "FORBIDDEN",
        "RATE_LIMIT_EXCEEDED",
        "INVALID_STATUS_TRANSITION",
        "ALREADY_PROCESSED",
        "INTERNAL_ERROR",
    }
)

# Candidate keys under which list endpoints may nest their items / total (pagination form is an
# assumption, Q-5). Helpers below accept any of them.
ITEM_KEYS = ("items", "data", "results")
TOTAL_KEYS = ("total", "count", "total_count")


class ErrorEnvelope(BaseModel):
    """Unified error response (brief §5.3). ``code`` membership is checked by assert helpers."""

    model_config = ConfigDict(extra="ignore")

    error: bool
    code: str
    message: str
    details: dict[str, Any] | None = None


def extract_items(body: Any) -> list[Any]:
    """Return the list of items from a paginated response (bare list or nested under a known key)."""
    if isinstance(body, list):
        return body
    if isinstance(body, dict):
        for key in ITEM_KEYS:
            if isinstance(body.get(key), list):
                return body[key]
    raise AssertionError(f"Could not locate a list of items in response body: {type(body)!r}")


def extract_total(body: Any) -> int | None:
    """Return the total count if the response exposes one, else None."""
    if isinstance(body, dict):
        for key in TOTAL_KEYS:
            if isinstance(body.get(key), int):
                return body[key]
    return None
