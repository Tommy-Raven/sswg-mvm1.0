"""Evaluation specification schema helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft202012Validator, RefResolver


def _load_schema(schema_path: Path) -> Dict[str, Any]:
    """Load a JSON schema from disk."""
    return json.loads(schema_path.read_text(encoding="utf-8"))


def get_evaluation_spec_validator(schema_dir: Path) -> Draft202012Validator:
    """Build a JSON schema validator for evaluation specs."""
    schema = _load_schema(schema_dir / "evaluation-spec.json")
    base_uri = schema_dir.as_uri().rstrip("/") + "/"
    resolver = RefResolver(base_uri=base_uri, referrer=schema)
    return Draft202012Validator(schema, resolver=resolver)


def validate_evaluation_spec(
    spec: Dict[str, Any],
    *,
    schema_dir: Path,
    spec_path: Path | None = None,
) -> List[Dict[str, Any]]:
    """Validate a spec payload and return a list of errors."""
    validator = get_evaluation_spec_validator(schema_dir)
    errors = sorted(validator.iter_errors(spec), key=lambda e: e.path)
    return [
        {
            "message": error.message,
            "path": list(error.path),
            "schema_path": list(error.schema_path),
            "spec_path": str(spec_path) if spec_path else None,
        }
        for error in errors
    ]
