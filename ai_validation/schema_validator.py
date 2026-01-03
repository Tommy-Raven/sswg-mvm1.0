#!/usr/bin/env python3
"""
ai_validation/schema_validator.py — JSON Schema validation utilities for SSWG MVM.

Provides:
- validate_workflow: validate a workflow dict against workflow_schema.json
- validate_template: validate a lightweight template dict against template_schema.json
- validate_json: generic JSON validation helper (optional schema)

Conventions:
- Schemas live under the sibling `schemas/` directory.
- Schemas declare `$schema` as JSON Schema Draft 2020-12.
- `$ref` values are relative filenames (e.g. "metadata_schema.json"),
  which are resolved against the local SCHEMAS_DIR.
- Core schema loading and validation helpers live in ai_cores/schema_core.py.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List

from jsonschema import ValidationError

from ai_cores.schema_core import get_validator, load_schema

logger = logging.getLogger("ai_validation.schema_validator")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)

# Root/schemas directory (ai_validation is sibling of schemas)
SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _load_schema(path: Path) -> Dict[str, Any]:
    """
    Load a JSON Schema file from disk into a Python dict.

    Args:
        path: Path to the schema file.

    Raises:
        FileNotFoundError: If the schema file does not exist.
        json.JSONDecodeError: If the schema file is not valid JSON.
    """
    return load_schema(path.parent, path.name)


def _get_validator(schema_name: str):
    """
    Construct a Draft 2020-12 validator for the given schema file.
    """
    return get_validator(SCHEMAS_DIR, schema_name)


def validate_workflow(
    workflow_obj: Any,
    schema_name: str = "workflow_schema.json",
) -> Tuple[bool, Optional[str]]:
    """
    Validate a workflow dict against the workflow schema.

    Returns:
        (ok, errors)
        ok: bool — True if validation passed (no errors, or schema missing)
        errors: formatted error message or None if no schema / no errors
    """
    if hasattr(workflow_obj, "to_dict"):
        workflow_obj = workflow_obj.to_dict()
    if not isinstance(workflow_obj, dict):
        raise TypeError("workflow_obj must be a dict or support to_dict()")

    try:
        validator = _get_validator(schema_name)
    except FileNotFoundError as e:
        logger.warning("Workflow schema not found: %s", e)
        # At MVM stage, treat missing schema as non-fatal and accept the object.
        return True, None

    errors = sorted(validator.iter_errors(workflow_obj), key=lambda e: e.path)
    if errors:
        for e in errors:
            logger.warning("Schema validation error: %s at %s", e.message, list(e.path))
        message = "; ".join(f"{e.message} at {list(e.path)}" for e in errors)
        return False, message

    logger.info(
        "Schema validation passed for workflow_id=%s",
        workflow_obj.get("workflow_id"),
    )
    return True, None


def validate_template(
    template_obj: Dict[str, Any],
    schema_name: str = "template_schema.json",
) -> Tuple[bool, Optional[List[ValidationError]]]:
    """
    Validate a lightweight workflow template dict against the template schema.

    Returns:
        (ok, errors)
        ok: bool — True if validation passed (no errors, or schema missing)
        errors: list[ValidationError] or None
    """
    try:
        validator = _get_validator(schema_name)
    except FileNotFoundError as e:
        logger.warning("Template schema not found: %s", e)
        # At MVM stage, treat missing schema as non-fatal and accept the object.
        return True, None

    errors = sorted(validator.iter_errors(template_obj), key=lambda e: e.path)
    if errors:
        for e in errors:
            logger.warning(
                "Template schema validation error: %s at %s",
                e.message,
                list(e.path),
            )
        return False, errors

    logger.info(
        "Template schema validation passed for template_id=%s",
        template_obj.get("template_id"),
    )
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
        obj:
            Any JSON-serializable object.
        schema_name:
            Optional schema filename in the schemas/ directory.

    Returns:
        bool: True if valid or no schema provided / missing, False if invalid.
    """
    if schema_name is None:
        # No schema provided → treat as valid in MVM
        return True

    try:
        validator = _get_validator(schema_name)
    except FileNotFoundError as e:
        logger.warning("Schema %s not found: %s", schema_name, e)
        # Soft-fail on missing schema at MVM stage
        return True

    errors = list(validator.iter_errors(obj))
    if errors:
        for e in errors:
            logger.warning(
                "JSON validation error (%s): %s at %s",
                schema_name,
                e.message,
                list(e.path),
            )
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
        print(f"Workflow has {len(errs or [])} schema issue(s); see logs.")
