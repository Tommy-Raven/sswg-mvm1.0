from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from ai_cores.cli_arg_parser_core import build_parser, parse_args
from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Validate run telemetry artifact.")
    parser.add_argument(
        "--telemetry-path",
        type=Path,
        default=Path("artifacts/telemetry/run_telemetry.json"),
        help="Telemetry artifact path.",
    )
    parser.add_argument(
        "--schema-path",
        type=Path,
        # GOVERNANCE SOURCE REMOVED
        # Canonical governance will be resolved from directive_core/docs/
        default=None,
        help="Telemetry schema path.",
    )
    parser.add_argument(
        "--run-id", type=str, default="telemetry-validate", help="Run identifier."
    )
    return parse_args(parser)


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/telemetry/failures"))
    if args.schema_path is None:
        emitter.emit(
            FailureLabel(
                Type="io_failure",
                message="Governance source removed: schema path must be supplied explicitly",
                phase_id="log",
                evidence={"schema_path": str(args.schema_path)},
            ),
            run_id=args.run_id,
        )
        print("Telemetry validation failed: missing schema path")
        return 1

    if not args.telemetry_path.exists():
        emitter.emit(
            FailureLabel(
                Type="reproducibility_failure",
                message="Telemetry artifact missing",
                phase_id="log",
                evidence={"path": str(args.telemetry_path)},
            ),
            run_id=args.run_id,
        )
        print("Telemetry validation failed: missing artifact")
        return 1

    telemetry = json.loads(args.telemetry_path.read_text(encoding="utf-8"))
    schema = json.loads(args.schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(telemetry), key=lambda e: e.path)
    if errors:
        emitter.emit(
            FailureLabel(
                Type="schema_failure",
                message="Telemetry schema validation failed",
                phase_id="log",
                evidence={
                    "errors": [
                        {
                            "message": error.message,
                            "path": list(error.path),
                            "schema_path": list(error.schema_path),
                        }
                        for error in errors
                    ]
                },
            ),
            run_id=args.run_id,
        )
        print("Telemetry validation failed")
        return 1

    print(f"Telemetry validation passed: {args.telemetry_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
