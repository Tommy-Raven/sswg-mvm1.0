#!/usr/bin/env python3
"""
generator/utils.py — Utility helpers for the SSWG generator.

Provides:
- generate_workflow_id() — unique, human-readable workflow IDs
- log() — structured console logger
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional


def generate_workflow_id(prefix: str = "workflow") -> str:
    """
    Generate a unique workflow identifier.

    Format:
        {prefix}_{8-hex}_{YYYYMMDDHHMMSS}
    """
    random_part = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{random_part}_{timestamp}"


def log(message: str, level: str = "INFO", extra: Optional[Dict[str, Any]] = None) -> None:
    """
    Structured console logger with timestamp and level.

    Args:
        message: Log message.
        level: Log severity label (e.g., INFO, WARN, ERROR).
        extra: Optional dict of additional fields for debugging.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if extra:
        print(f"[{level}] {timestamp} — {message} | extra={extra}")
    else:
        print(f"[{level}] {timestamp} — {message}")
