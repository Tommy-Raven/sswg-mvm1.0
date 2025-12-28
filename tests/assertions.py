"""Assertion helpers for test expectations without using assert statements."""

from __future__ import annotations


def require(condition: bool, message: str = "Assertion failed") -> None:
    """Raise AssertionError when condition is False."""
    if not condition:
        raise AssertionError(message)
