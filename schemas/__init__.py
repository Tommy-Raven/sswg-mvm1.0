#!/usr/bin/env python3
"""
schemas/__init__.py — SSWG-MVM JSON Schema package

This module provides a lightweight, centralized interface for working with the
JSON Schemas defined under the `schemas/` directory.

Responsibilities (MVM level):
- Expose the schemas directory path (`SCHEMAS_DIR`)
- Provide simple helpers to:
  - list available schema files
  - resolve a schema name to a Path
  - load a schema as a Python dict

Higher-level discovery and validation logic lives in:
- ai_validation/schema_tracker.py
- ai_validation/schema_validator.py

This module is intentionally thin to avoid circular dependencies and to keep
the `schemas` package focused on data + basic utilities.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

# Root directory for all JSON Schema files in this package
SCHEMAS_DIR: Path = Path(__file__).resolve().parent


def list_schemas() -> List[str]:
    """
    List all available JSON Schema filenames in the schemas directory.

    Returns:
        A sorted list of schema filenames, e.g.:
        ["workflow_schema.json", "phase_schema.json", ...]
    """
    if not SCHEMAS_DIR.exists():
        return []
    return sorted(p.name for p in SCHEMAS_DIR.glob("*.json") if p.is_file())


def get_schema_path(schema_name: str) -> Optional[Path]:
    """
    Resolve a schema filename to an absolute Path under the schemas directory.

    Args:
        schema_name:
            Filename of the schema, e.g. "workflow_schema.json".

    Returns:
        Path to the schema file if it exists, otherwise None.
    """
    path = SCHEMAS_DIR / schema_name
    return path if path.exists() else None


def load_schema(schema_name: str) -> Dict:
    """
    Load a JSON Schema by filename.

    Args:
        schema_name:
            Filename of the schema in the schemas directory.

    Returns:
        The parsed JSON Schema as a Python dict.

    Raises:
        FileNotFoundError: If the schema file does not exist.
        json.JSONDecodeError: If the schema file is not valid JSON.
    """
    path = get_schema_path(schema_name)
    if path is None:
        raise FileNotFoundError(f"Schema file not found: {schema_name}")
    return json.loads(path.read_text(encoding="utf-8"))


__all__ = [
    "SCHEMAS_DIR",
    "list_schemas",
    "get_schema_path",
    "load_schema",
]
