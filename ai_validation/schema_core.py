#!/usr/bin/env python3
"""
ai_validation/schema_core.py — Shared JSON Schema validation core.

Provides centralized schema loading, validator construction, and artifact
validation for deterministic enforcement.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from jsonschema import Draft202012Validator, RefResolver

__all__ = ["load_schema", "get_validator", "validate_artifact"]


def load_schema(schema_dir: Path, schema_name: str) -> Dict[str, Any]:
    """Load a JSON schema from disk."""
    schema_path = schema_dir / schema_name
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def get_validator(schema_dir: Path, schema_name: str) -> Draft202012Validator:
    """Build a Draft 2020-12 validator with local $ref resolution."""
    schema_dir = schema_dir.resolve()
    schema = load_schema(schema_dir, schema_name)
    store: Dict[str, Any] = {}
    for path in schema_dir.rglob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if "$id" in payload:
            store[payload["$id"].rstrip("#")] = payload
    base_uri = schema_dir.as_uri().rstrip("/") + "/"
    resolver = RefResolver(base_uri=base_uri, referrer=schema, store=store)
    return Draft202012Validator(schema, resolver=resolver)


def validate_artifact(
    payload: Any,
    schema_dir: Path,
    schema_name: str,
) -> List[Dict[str, Any]]:
    """Validate payload against schema and return normalized error entries."""
    validator = get_validator(schema_dir, schema_name)
    errors = sorted(validator.iter_errors(payload), key=lambda e: e.path)
    return [
        {
            "message": error.message,
            "path": list(error.path),
            "schema_path": list(error.schema_path),
        }
        for error in errors
    ]
