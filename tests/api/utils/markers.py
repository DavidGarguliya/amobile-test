"""Traceability marker: link a test to requirement IDs from REQUIREMENTS.md.

Usage::

    from tests.api.utils.markers import req

    @req("FR-T11", "INV-P5")
    def test_status_transition_forbidden_new_to_resolved(...):
        ...

The ``req`` marker is registered in ``pytest.ini``; its args are the requirement/invariant IDs.
"""

from __future__ import annotations

import pytest


def req(*ids: str):
    """Attach requirement/invariant IDs to a test for traceability (TEST_PLAN §5)."""
    return pytest.mark.req(*ids)
