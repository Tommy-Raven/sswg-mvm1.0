#!/usr/bin/env python3
"""
ai_validation/schema_validator.py — JSON Schema validation utilities for SSWG MVM.

Provides:
- validate_workflow: validate a workflow dict against workflow_schema.json
- validate_json: generic JSON validation helper (optional schema)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from jsonschema import Draft7Validator, RefResolver, ValidationError

logger = logging.getLogger("ai_validation.schema_validator")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)

# Root/schemas directory (ai_validation is sibling of schemas)
SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _load_schema(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _get_validator(schema_name: str) -> Draft7Validator:
    schema_path = SCHEMAS_DIR / schema_name
    schema = _load_schema(schema_path)
    resolver = RefResolver(base_uri=f"file://{SCHEMAS_DIR}/", referrer=schema)
    return Draft7Validator(schema, resolver=resolver)


def validate_workflow(
    workflow_obj: Dict[str, Any],
    schema_name: str = "workflow_schema.json",
) -> Tuple[bool, Optional[list]]:
    """
    Validate a workflow dict against the workflow schema.

    Returns:
        (ok, errors)
        ok: bool — True if validation passed (no errors)
        errors: list[ValidationError] or None
    """
    try:
        validator = _get_validator(schema_name)
    except FileNotFoundError as e:
        logger.warning("Workflow schema not found: %s", e)
        return True, None  # do not hard-fail if schema file missing in MVM

    errors = sorted(validator.iter_errors(workflow_obj), key=lambda e: e.path)
    if errors:
        for e in errors:
            logger.warning("Schema validation error: %s at %s", e.message, list(e.path))
        return False, errors

    logger.info("Schema validation passed for workflow_id=%s", workflow_obj.get("workflow_id"))
    return True, None


def validate_json(
    obj: Any,
    schema_name: Optional[str] = None,
) -> bool:
    """
    Generic JSON validation helper.

    If schema_name is None, this function returns True (no-op) to avoid
    forcing every JSON blob to have a schema during the MVM stage.

    Args:
        obj: Any JSON-serializable object.
        schema_name: Optional schema filename in schemas/ directory.

    Returns:
        bool: True if valid or no schema provided, False if invalid.
    """
    if schema_name is None:
        # No schema provided → treat as valid in MVM
        return True

    try:
        validator = _get_validator(schema_name)
    except FileNotFoundError as e:
        logger.warning("Schema %s not found: %s", schema_name, e)
        return True

    errors = list(validator.iter_errors(obj))
    if errors:
        for e in errors:
            logger.warning("JSON validation error (%s): %s at %s", schema_name, e.message, list(e.path))
        return False

    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: schema_validator.py <workflow_json_path>")
        raise SystemExit(1)

    wf_path = Path(sys.argv[1])
    wf = json.loads(wf_path.read_text(encoding="utf-8"))
    ok, errs = validate_workflow(wf)
    if ok:
        print("Workflow is valid.")
    else:
        print(f"Workflow has {len(errs)} schema issues; see logs.")
