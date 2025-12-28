from __future__ import annotations

import argparse
import json
from pathlib import Path

from generator.failure_emitter import FailureEmitter, FailureLabel
from generator.overlay_governance import validate_overlay_descriptor


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate overlay descriptor.")
    parser.add_argument("overlay_path", type=Path, help="Overlay descriptor JSON path.")
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
    overlay = json.loads(args.overlay_path.read_text(encoding="utf-8"))
    errors = validate_overlay_descriptor(
        overlay,
        schema_dir=args.schema_dir,
        overlay_path=args.overlay_path,
    )
    if errors:
        evidence = {"errors": errors}
        failure = FailureLabel(
            Type="schema_failure",
            message="Overlay descriptor validation failed",
            phase_id="validate",
            evidence=evidence,
        )
        FailureEmitter(Path("artifacts/failures")).emit(failure, run_id=args.run_id)
        print(f"Overlay validation failed: {failure.as_dict()}")
        return 1
    print(f"Overlay validation passed: {args.overlay_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
