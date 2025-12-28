from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

from generator.failure_emitter import FailureEmitter, FailureLabel


def _get_validator(schema_dir: Path) -> Draft202012Validator:
    schema = json.loads(
        (schema_dir / "experiment-scope.json").read_text(encoding="utf-8")
    )
    base_uri = schema_dir.as_uri().rstrip("/") + "/"
    return Draft202012Validator(
        schema, resolver=RefResolver(base_uri=base_uri, referrer=schema)
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate experiment scope declaration."
    )
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
    return parser.parse_args()


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
    validator = _get_validator(args.schema_dir)
    errors = sorted(validator.iter_errors(scope), key=lambda e: e.path)
    if errors:
        failure = FailureLabel(
            Type="schema_failure",
            message="Experiment scope validation failed",
            phase_id="validate",
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
        )
        FailureEmitter(Path("artifacts/failures")).emit(failure, run_id=args.run_id)
        print(f"Experiment scope validation failed: {failure.as_dict()}")
        return 1

    print(f"Experiment scope validation passed: {args.scope_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
