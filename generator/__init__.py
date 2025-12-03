#!/usr/bin/env python3
"""
generator package — top-level entrypoints for SSWG workflow generation.

This package ties together:
- CLI entrypoint
- ID generation and logging utilities
"""

from __future__ import annotations

from .main import main as cli_main  # CLI entrypoint
from .utils import generate_workflow_id, log

__all__ = [
    "cli_main",
    "generate_workflow_id",
    "log",
]


def get_version() -> str:
    """Return a simple version identifier for the generator subsystem."""
    return "generator-mvm-0.1.0"
