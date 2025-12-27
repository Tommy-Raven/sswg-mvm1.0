"""Hashing helpers for canonical payloads."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonicalize_json(data: Any) -> str:
    """Serialize JSON deterministically for hashing."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def hash_data(data: Any) -> str:
    """Return a SHA-256 hash for a canonicalized payload."""
    payload = canonicalize_json(data).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
