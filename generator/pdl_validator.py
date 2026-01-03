"""
generator/pdl_validator.py — PDL schema validation for SSWG MVM.

Validates a PDL object or YAML file against the PDL phase set schema and
emits deterministic failure labels on schema or IO errors.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from jsonschema import Draft202012Validator

from ai_validation.schema_core import get_validator, load_schema
from cli.cli_arg_parser_core import build_parser, parse_args

from generator.failure_emitter import FailureEmitter, FailureLabel
from generator.hashing import hash_data

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"
PHASE_CONSTRAINTS_PATH = SCHEMAS_DIR / "phase_constraints.yaml"


@dataclass
class PDLFailureLabel:  # pylint: disable=invalid-name
    """Failure label used by PDL validation."""

    Type: str
    message: str
    phase_id: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        """Return the label as a serializable dictionary."""
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
    """Raised when PDL validation fails."""

    def __init__(self, label: PDLFailureLabel) -> None:
        super().__init__(label.message)
        self.label = label


def _load_schema(schema_dir: Path, schema_name: str) -> Dict[str, Any]:
    """Load a JSON schema from disk."""
    return load_schema(schema_dir, schema_name)


def _get_validator(schema_dir: Path, schema_name: str) -> Draft202012Validator:
    """Build a JSON schema validator with a local ref store."""
    return get_validator(schema_dir, schema_name)


def _load_pdl_yaml(path: Path) -> Dict[str, Any]:
    """Load a PDL YAML/JSON file and return it as a mapping."""
    payload = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(payload)
    else:
        data = yaml.safe_load(payload)
    if not isinstance(data, dict):
        raise ValueError("PDL document must parse to a mapping object")
    return data


def _load_phase_constraints(schema_dir: Path) -> Dict[str, Any]:
    """Load the phase constraints mapping from disk."""
    constraints_path = schema_dir / PHASE_CONSTRAINTS_PATH.name
    if not constraints_path.exists():
        raise PDLValidationError(
            PDLFailureLabel(
                Type="io_failure",
                message="Phase constraints file not found",
                evidence={"path": str(constraints_path)},
            )
        )
    try:
        payload = yaml.safe_load(constraints_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise PDLValidationError(
            PDLFailureLabel(
                Type="io_failure",
                message=str(exc),
                evidence={"path": str(constraints_path)},
            )
        ) from exc
    if not isinstance(payload, dict):
        raise PDLValidationError(
            PDLFailureLabel(
                Type="schema_failure",
                message="Phase constraints document must be a mapping",
                evidence={"path": str(constraints_path)},
            )
        )
    phases = payload.get("phases")
    if not isinstance(phases, dict):
        raise PDLValidationError(
            PDLFailureLabel(
                Type="schema_failure",
                message="Phase constraints missing required phases mapping",
                evidence={"path": str(constraints_path)},
            )
        )
    return phases


def _validate_phase_constraints(
    phases: list[dict[str, Any]],
    *,
    schema_dir: Path,
) -> None:
    phase_constraints = _load_phase_constraints(schema_dir)
    phase_map = {
        phase.get("name"): phase for phase in phases if isinstance(phase, dict)
    }
    for phase_name, constraints_spec in phase_constraints.items():
        if phase_name not in phase_map:
            raise PDLValidationError(
                PDLFailureLabel(
                    Type="schema_failure",
                    message="PDL missing phase required by phase constraints",
                    evidence={"phase": phase_name},
                )
            )
        if not isinstance(constraints_spec, dict):
            raise PDLValidationError(
                PDLFailureLabel(
                    Type="schema_failure",
                    message="Phase constraints entry must be a mapping",
                    evidence={"phase": phase_name},
                )
            )
        determinism = constraints_spec.get("determinism")
        determinism_required = constraints_spec.get("determinism_required")
        if determinism not in {"deterministic", "nondeterministic"}:
            raise PDLValidationError(
                PDLFailureLabel(
                    Type="schema_failure",
                    message="Phase constraints determinism must be deterministic or nondeterministic",
                    evidence={"phase": phase_name, "determinism": determinism},
                )
            )
        if not isinstance(determinism_required, bool):
            raise PDLValidationError(
                PDLFailureLabel(
                    Type="schema_failure",
                    message="Phase constraints determinism_required must be boolean",
                    evidence={
                        "phase": phase_name,
                        "determinism_required": determinism_required,
                    },
                )
            )
        phase_constraints_payload = phase_map[phase_name].get("constraints", {})
        if determinism_required:
            if phase_constraints_payload.get("deterministic_required") is not True:
                raise PDLValidationError(
                    PDLFailureLabel(
                        Type="schema_failure",
                        message="Determinism required for phase",
                        evidence={"phase": phase_name},
                    )
                )
        elif phase_constraints_payload.get("deterministic_required") is True:
            raise PDLValidationError(
                PDLFailureLabel(
                    Type="schema_failure",
                    message="Determinism must not be required for phase",
                    evidence={"phase": phase_name},
                )
            )
        if determinism == "nondeterministic":
            if (
                phase_constraints_payload.get("output_must_be_labeled_nondeterministic")
                is not True
            ):
                raise PDLValidationError(
                    PDLFailureLabel(
                        Type="schema_failure",
                        message="Nondeterministic phases must be labeled as nondeterministic",
                        evidence={"phase": phase_name},
                    )
                )


def _validate_handler_paths(phases: list[dict[str, Any]]) -> None:
    for phase in phases:
        handler_path = phase.get("handler")
        phase_name = phase.get("name", "unknown")
        if not handler_path:
            raise PDLValidationError(
                PDLFailureLabel(
                    Type="schema_failure",
                    message="Missing handler declaration in PDL phase",
                    evidence={"phase": phase_name},
                )
            )
        module_path, _, attribute = handler_path.rpartition(".")
        if not module_path or not attribute:
            raise PDLValidationError(
                PDLFailureLabel(
                    Type="schema_failure",
                    message="Invalid handler path format",
                    evidence={"phase": phase_name, "handler": handler_path},
                )
            )
        if find_spec(module_path) is None:
            raise PDLValidationError(
                PDLFailureLabel(
                    Type="schema_failure",
                    message="Handler module not found",
                    evidence={"phase": phase_name, "handler": handler_path},
                )
            )
        module = import_module(module_path)
        handler = getattr(module, attribute, None)
        if handler is None or not callable(handler):
            raise PDLValidationError(
                PDLFailureLabel(
                    Type="schema_failure",
                    message="Handler not callable",
                    evidence={"phase": phase_name, "handler": handler_path},
                )
            )


def validate_pdl_object(
    pdl_obj: Dict[str, Any],
    *,
    schema_dir: Path = SCHEMAS_DIR,
    schema_name: str = "pdl.json",
    resolve_handlers: bool = True,
) -> None:
    """Validate a PDL object against the schema."""
    try:
        validator = _get_validator(schema_dir, schema_name)
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
    phases = pdl_obj.get("phases", [])
    if isinstance(phases, list):
        _validate_phase_constraints(phases, schema_dir=schema_dir)
    if resolve_handlers and isinstance(phases, list):
        _validate_handler_paths(phases)


def validate_pdl_file(
    path: Path,
    *,
    schema_dir: Path = SCHEMAS_DIR,
    schema_name: str = "pdl.json",
    resolve_handlers: bool = True,
) -> None:
    """Validate a PDL YAML file against the schema."""
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

    validate_pdl_object(
        pdl_obj,
        schema_dir=schema_dir,
        schema_name=schema_name,
        resolve_handlers=resolve_handlers,
    )


def validate_pdl_file_with_report(
    *,
    pdl_path: Path,
    schema_dir: Path = SCHEMAS_DIR,
    report_dir: Path,
    run_id: str,
    resolve_handlers: bool = True,
) -> None:
    """Validate a PDL file and emit a validation report."""
    schema_path = schema_dir / "pdl.json"
    try:
        validate_pdl_file(
            pdl_path,
            schema_dir=schema_dir,
            resolve_handlers=resolve_handlers,
        )
    except PDLValidationError as exc:
        label = FailureLabel(
            Type=exc.label.Type,
            message=exc.label.message,
            phase_id="validate",
            evidence=exc.label.evidence,
        )
        FailureEmitter(report_dir / "failures").emit(label, run_id=run_id)
        _write_validation_report(
            pdl_path=pdl_path,
            schema_path=schema_path,
            result="fail",
            errors=label.evidence.get("errors", []) if label.evidence else [],
            report_dir=report_dir,
            run_id=run_id,
        )
        raise
    _write_validation_report(
        pdl_path=pdl_path,
        schema_path=schema_path,
        result="pass",
        errors=[],
        report_dir=report_dir,
        run_id=run_id,
    )


def _write_validation_report(
    *,
    pdl_path: Path,
    schema_path: Path,
    result: str,
    errors: list[dict[str, Any]],
    report_dir: Path,
    run_id: str,
) -> Path:
    """Write a validation report payload to disk."""
    report_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "anchor": {
            "anchor_id": "pdl_validation_report",
            "anchor_version": "1.0.0",
            "scope": "validation",
            "owner": "generator.pdl_validator",
            "status": "draft",
        },
        "pdl_path": str(pdl_path),
        "schema_path": str(schema_path),
        "result": result,
        "errors": errors,
        "run_id": run_id,
        "inputs_hash": hash_data({"pdl": str(pdl_path), "schema": str(schema_path)}),
    }
    report_path = report_dir / f"pdl_validation_{payload['inputs_hash']}.json"
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return report_path


def _parse_args() -> argparse.Namespace:
    """Parse command line arguments for PDL validation."""
    parser = build_parser("Validate a PDL YAML file against the PDL schema.")
    parser.add_argument(
        "pdl_path",
        type=Path,
        help="Path to the PDL YAML file to validate.",
    )
    parser.add_argument(
        "schema_dir",
        nargs="?",
        default=SCHEMAS_DIR,
        type=Path,
        help="Directory containing schema files (default: schemas).",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=Path("artifacts/validation"),
        help="Directory to emit validation reports.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="local-run",
        help="Run identifier for report and failure log output.",
    )
    parser.add_argument(
        "--resolve-handlers",
        dest="resolve_handlers",
        action="store_true",
        default=True,
        help="Resolve handler paths after schema validation (default: enabled).",
    )
    parser.add_argument(
        "--no-resolve-handlers",
        dest="resolve_handlers",
        action="store_false",
        help="Disable handler resolution checks.",
    )
    return parse_args(parser)


def _main() -> int:
    args = _parse_args()
    pdl_path = args.pdl_path
    schema_dir = args.schema_dir
    report_dir = args.report_dir
    run_id = args.run_id
    schema_path = schema_dir / "pdl.json"
    try:
        validate_pdl_file(
            pdl_path,
            schema_dir=schema_dir,
            resolve_handlers=args.resolve_handlers,
        )
    except PDLValidationError as exc:
        label = FailureLabel(
            Type=exc.label.Type,
            message=exc.label.message,
            phase_id="validate",
            evidence=exc.label.evidence,
        )
        FailureEmitter(report_dir / "failures").emit(label, run_id=run_id)
        _write_validation_report(
            pdl_path=pdl_path,
            schema_path=schema_path,
            result="fail",
            errors=label.evidence.get("errors", []) if label.evidence else [],
            report_dir=report_dir,
            run_id=run_id,
        )
        print(f"PDL validation failed: {label.as_dict()}")
        return 1
    _write_validation_report(
        pdl_path=pdl_path,
        schema_path=schema_path,
        result="pass",
        errors=[],
        report_dir=report_dir,
        run_id=run_id,
    )
    print(f"PDL validation passed: {pdl_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
