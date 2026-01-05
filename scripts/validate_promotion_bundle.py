from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from ai_cores.cli_arg_parser_core import build_parser, parse_args
from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Validate promotion bundle completeness.")
    parser.add_argument(
        "--checklist-path",
        type=Path,
        # GOVERNANCE SOURCE REMOVED
        # Canonical governance will be resolved from directive_core/docs/
        default=None,
        help="Promotion checklist path.",
    )
    parser.add_argument(
        "--protocol-path",
        type=Path,
        # GOVERNANCE SOURCE REMOVED
        # Canonical governance will be resolved from directive_core/docs/
        default=None,
        help="Promotion protocol path.",
    )
    parser.add_argument(
        "--waiver-paths",
        type=Path,
        nargs="*",
        default=[],
        help="Optional waiver record paths.",
    )
    parser.add_argument(
        "--evidence-paths",
        type=Path,
        nargs="+",
        required=True,
        help="Evidence artifact paths required for promotion.",
    )
    parser.add_argument(
        "--schema-dir",
        type=Path,
        # GOVERNANCE SOURCE REMOVED
        # Canonical governance will be resolved from directive_core/docs/
        default=None,
        help="Schema directory.",
    )
    parser.add_argument(
        "--run-id", type=str, default="promotion-validate", help="Run identifier."
    )
    return parse_args(parser)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_schema(path: Path, schema_path: Path) -> list[dict]:
    payload = _load_json(path)
    schema = _load_json(schema_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: e.path)
    return [
        {
            "message": error.message,
            "path": list(error.path),
            "schema_path": list(error.schema_path),
        }
        for error in errors
    ]


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/failures"))
    if args.checklist_path is None or args.protocol_path is None or args.schema_dir is None:
        emitter.emit(
            FailureLabel(
                Type="io_failure",
                message="Governance source removed: required paths must be supplied explicitly",
                phase_id="validate",
                evidence={
                    "checklist_path": str(args.checklist_path),
                    "protocol_path": str(args.protocol_path),
                    "schema_dir": str(args.schema_dir),
                },
            ),
            run_id=args.run_id,
        )
        print("Promotion bundle validation failed")
        return 1

    missing = [str(path) for path in args.evidence_paths if not path.exists()]
    if missing:
        emitter.emit(
            FailureLabel(
                Type="reproducibility_failure",
                message="Promotion bundle missing evidence artifacts",
                phase_id="validate",
                evidence={"missing": missing},
            ),
            run_id=args.run_id,
        )
        print("Promotion bundle validation failed")
        return 1

    checklist_errors = _validate_schema(
        args.checklist_path, args.schema_dir / "promotion-checklist.json"
    )
    if checklist_errors:
        emitter.emit(
            FailureLabel(
                Type="schema_failure",
                message="Promotion checklist schema validation failed",
                phase_id="validate",
                evidence={"errors": checklist_errors},
            ),
            run_id=args.run_id,
        )
        print("Promotion bundle validation failed")
        return 1

    protocol = _load_json(args.protocol_path)
    non_waivable = protocol.get("blocking_conditions", {}).get("non_waivable", [])

    for waiver_path in args.waiver_paths:
        waiver_errors = _validate_schema(
            waiver_path, args.schema_dir / "waiver-record.json"
        )
        if waiver_errors:
            emitter.emit(
                FailureLabel(
                    Type="schema_failure",
                    message="Waiver record schema validation failed",
                    phase_id="validate",
                    evidence={"errors": waiver_errors},
                ),
                run_id=args.run_id,
            )
            print("Promotion bundle validation failed")
            return 1
        waiver = _load_json(waiver_path)
        if waiver.get("gate_id") in non_waivable:
            emitter.emit(
                FailureLabel(
                    Type="schema_failure",
                    message="Waiver applied to non-waivable gate",
                    phase_id="validate",
                    evidence={"gate_id": waiver.get("gate_id")},
                ),
                run_id=args.run_id,
            )
            print("Promotion bundle validation failed")
            return 1

    print("Promotion bundle validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
