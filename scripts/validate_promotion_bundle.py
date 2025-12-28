from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate promotion bundle completeness."
    )
    parser.add_argument(
        "--checklist-path",
        type=Path,
        default=Path("artifacts/governance/promotion_checklist.json"),
        help="Promotion checklist path.",
    )
    parser.add_argument(
        "--protocol-path",
        type=Path,
        default=Path("governance/canon_promotion_protocol.json"),
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
        default=Path("schemas"),
        help="Schema directory.",
    )
    parser.add_argument(
        "--run-id", type=str, default="promotion-validate", help="Run identifier."
    )
    return parser.parse_args()


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
    emitter = FailureEmitter(Path("artifacts/governance/failures"))

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
