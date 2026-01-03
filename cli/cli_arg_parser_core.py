"""
cli_arg_parser_core.py — Shared argument parsing for validation scripts.

This module centralizes parser construction and argument normalization for
validation entrypoints.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, Iterable

__all__ = ["build_parser", "parse_args", "normalize_args"]


def build_parser(description: str) -> argparse.ArgumentParser:
    """Create a baseline parser for validation entrypoints."""
    return argparse.ArgumentParser(
        description=f"{description} (argument parsing via cli_arg_parser_core)."
    )


def normalize_args(args: argparse.Namespace) -> argparse.Namespace:
    """Normalize parsed arguments for consistent validation execution."""
    for key, value in vars(args).items():
        if isinstance(value, Path):
            setattr(args, key, value.expanduser())
        elif isinstance(value, list):
            setattr(args, key, _normalize_iterable(value))
    if hasattr(args, "run_id") and getattr(args, "run_id") in (None, ""):
        env_run_id = os.environ.get("RUN_ID")
        if env_run_id:
            setattr(args, "run_id", env_run_id)
    return args


def _normalize_iterable(values: Iterable[Any]) -> list[Any]:
    normalized: list[Any] = []
    for item in values:
        if isinstance(item, Path):
            normalized.append(item.expanduser())
        else:
            normalized.append(item)
    return normalized


def parse_args(parser: argparse.ArgumentParser, argv: list[str] | None = None) -> argparse.Namespace:
    """Parse and normalize arguments using the shared core."""
    return normalize_args(parser.parse_args(argv))
