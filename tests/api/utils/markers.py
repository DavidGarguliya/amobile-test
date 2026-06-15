"""Traceability marker: link a test to requirement IDs from REQUIREMENTS.md.

Usage::

    from tests.api.utils.markers import req

    @req("FR-T11", "INV-P5")
    def test_status_transition_forbidden_new_to_resolved(...):
        ...

``req`` attaches a pytest marker (``--strict-markers`` registered in pytest.ini) AND, when Allure is
installed, an Allure ``tag`` plus a ``requirement`` label per ID — so the IDs show up in the report.
"""

from __future__ import annotations

import pytest

try:
    import allure
except ImportError:  # pragma: no cover
    allure = None  # type: ignore[assignment]


def req(*ids: str):
    """Attach requirement/invariant IDs to a test for traceability (TEST_PLAN §5)."""

    def decorator(func):
        func = pytest.mark.req(*ids)(func)
        if allure is not None:
            for rid in ids:
                func = allure.tag(rid)(func)
                func = allure.label("requirement", rid)(func)
        return func

    return decorator
