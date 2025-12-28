from __future__ import annotations

import argparse
import json
from pathlib import Path

from generator.evaluation_spec import validate_evaluation_spec
from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate evaluation spec.")
    parser.add_argument("spec_path", type=Path, help="Evaluation spec JSON path.")
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
    if not args.spec_path.exists():
        failure = FailureLabel(
            Type="reproducibility_failure",
            message="Evaluation spec is missing",
            phase_id="validate",
            evidence={"path": str(args.spec_path)},
        )
        FailureEmitter(Path("artifacts/failures")).emit(failure, run_id=args.run_id)
        print(f"Evaluation spec validation failed: {failure.as_dict()}")
        return 1

    spec = json.loads(args.spec_path.read_text(encoding="utf-8"))
    errors = validate_evaluation_spec(
        spec, schema_dir=args.schema_dir, spec_path=args.spec_path
    )
    if errors:
        failure = FailureLabel(
            Type="schema_failure",
            message="Evaluation spec validation failed",
            phase_id="validate",
            evidence={"errors": errors},
        )
        FailureEmitter(Path("artifacts/failures")).emit(failure, run_id=args.run_id)
        print(f"Evaluation spec validation failed: {failure.as_dict()}")
        return 1

    print(f"Evaluation spec validation passed: {args.spec_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
