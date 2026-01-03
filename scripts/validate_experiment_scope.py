from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_validation.schema_core import validate_artifact

from cli.cli_arg_parser_core import build_parser, parse_args
from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Validate experiment scope declaration.")
    parser.add_argument("scope_path", type=Path, help="Experiment scope JSON path.")
    parser.add_argument(
        "--schema-dir",
        type=Path,
        default=Path("schemas"),
        help="Schema directory.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="local-run",
        help="Run identifier for failure logs.",
    )
    return parse_args(parser)


def main() -> int:
    args = _parse_args()
    if not args.scope_path.exists():
        failure = FailureLabel(
            Type="schema_failure",
            message="Experiment scope declaration is missing",
            phase_id="validate",
            evidence={"path": str(args.scope_path)},
        )
        FailureEmitter(Path("artifacts/failures")).emit(failure, run_id=args.run_id)
        print(f"Experiment scope validation failed: {failure.as_dict()}")
        return 1

    scope = json.loads(args.scope_path.read_text(encoding="utf-8"))
    errors = validate_artifact(scope, args.schema_dir, "experiment-scope.json")
    if errors:
        failure = FailureLabel(
            Type="schema_failure",
            message="Experiment scope validation failed",
            phase_id="validate",
            evidence={
                "errors": errors
            },
        )
        FailureEmitter(Path("artifacts/failures")).emit(failure, run_id=args.run_id)
        print(f"Experiment scope validation failed: {failure.as_dict()}")
        return 1

    print(f"Experiment scope validation passed: {args.scope_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
