#!/usr/bin/env python3
"""Validate root contract yaml files against json schemas."""

from __future__ import annotations


def validate_contracts() -> int:
    # GOVERNANCE SOURCE REMOVED
    # Canonical governance will be resolved from directive_core/docs/
    print("root contract validation failed: governance sources must be supplied explicitly")
    return 1


if __name__ == "__main__":
    raise SystemExit(validate_contracts())
