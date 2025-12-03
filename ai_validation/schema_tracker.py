#!/usr/bin/env python3
"""
ai_validation/schema_tracker.py — Schema discovery utilities for SSWG MVM.

Responsibilities (MVM level):

- Locate the `schemas/` directory.
- List available JSON schema files.
- Resolve schema names to concrete file paths.
- Optionally inspect schemas for version / id metadata.

This is intentionally lightweight; it can be extended later to emit telemetry
or maintain a persistent registry.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


def list_schemas() -> List[str]:
    """
    List all available schema files (filenames) in the schemas directory.

    Returns:
        List of schema filenames, e.g. ["workflow_schema.json", "module_schema.json"].
    """
    if not SCHEMAS_DIR.exists():
        return []
    return sorted(
        p.name for p in SCHEMAS_DIR.glob("*.json") if p.is_file()
    )


def get_schema_path(schema_name: str) -> Optional[Path]:
    """
    Resolve a schema name to a concrete path in the schemas directory.

    Args:
        schema_name: Filename of the schema, e.g. "workflow_schema.json".

    Returns:
        Path to schema file, or None if it does not exist.
    """
    path = SCHEMAS_DIR / schema_name
    return path if path.exists() else None


def schema_exists(schema_name: str) -> bool:
    """
    Check whether a schema exists in the schemas directory.
    """
    return get_schema_path(schema_name) is not None


def _load_schema(path: Path) -> Dict:
    """Internal helper: load a JSON schema from path."""
    return json.loads(path.read_text(encoding="utf-8"))


def get_schema_metadata(schema_name: str) -> Optional[Dict]:
    """
    Inspect a schema file and return basic metadata, if available.

    Looks for common fields like:
    - "$id"
    - "title"
    - "version"

    Args:
        schema_name: Filename of the schema.

    Returns:
        Dict with metadata, or None if file missing or unreadable.
    """
    path = get_schema_path(schema_name)
    if path is None:
        return None

    try:
        obj = _load_schema(path)
    except Exception:
        return None

    meta = {
        "id": obj.get("$id"),
        "title": obj.get("title"),
        "version": obj.get("version"),
        "file": str(path),
    }
    return meta


if __name__ == "__main__":
    # Tiny self-test
    print("Schemas dir:", SCHEMAS_DIR)
    print("Available schemas:", list_schemas())
    for name in list_schemas():
        print("  -", name, "meta:", get_schema_metadata(name))
# End of ai_validation/schema_tracker.py