"""
generator/pdl_validator.py — PDL schema validation for SSWG MVM.

Validates a PDL object or YAML file against the PDL phase set schema and
emits deterministic failure labels on schema or IO errors.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from jsonschema import Draft202012Validator, RefResolver, ValidationError

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


@dataclass
class PDLFailureLabel:
    Type: str
    message: str
    phase_id: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "Type": self.Type,
            "message": self.message,
        }
        if self.phase_id is not None:
            payload["phase_id"] = self.phase_id
        if self.evidence is not None:
            payload["evidence"] = self.evidence
        return payload


class PDLValidationError(RuntimeError):
    def __init__(self, label: PDLFailureLabel) -> None:
        super().__init__(label.message)
        self.label = label


def _load_schema(schema_name: str) -> Dict[str, Any]:
    schema_path = SCHEMAS_DIR / schema_name
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _get_validator(schema_name: str) -> Draft202012Validator:
    schema = _load_schema(schema_name)
    base_uri = SCHEMAS_DIR.as_uri().rstrip("/") + "/"
    resolver = RefResolver(base_uri=base_uri, referrer=schema)
    return Draft202012Validator(schema, resolver=resolver)


def _load_pdl_yaml(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("PDL YAML must parse to a mapping object")
    return data


def validate_pdl_object(pdl_obj: Dict[str, Any], schema_name: str = "pdl.json") -> None:
    try:
        validator = _get_validator(schema_name)
    except FileNotFoundError as exc:
        raise PDLValidationError(
            PDLFailureLabel(
                Type="io_failure",
                message=str(exc),
                evidence={"schema": schema_name},
            )
        ) from exc

    errors = sorted(validator.iter_errors(pdl_obj), key=lambda e: e.path)
    if errors:
        details = [
            {
                "message": error.message,
                "path": list(error.path),
                "schema_path": list(error.schema_path),
            }
            for error in errors
        ]
        raise PDLValidationError(
            PDLFailureLabel(
                Type="schema_failure",
                message="PDL schema validation failed",
                evidence={"errors": details},
            )
        )


def validate_pdl_file(path: Path, schema_name: str = "pdl.json") -> None:
    try:
        pdl_obj = _load_pdl_yaml(path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        raise PDLValidationError(
            PDLFailureLabel(
                Type="io_failure",
                message=str(exc),
                evidence={"path": str(path)},
            )
        ) from exc

    validate_pdl_object(pdl_obj, schema_name=schema_name)
