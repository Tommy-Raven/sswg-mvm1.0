from __future__ import annotations

import argparse
import json
from pathlib import Path

from generator.failure_emitter import FailureEmitter, FailureLabel
from generator.overlay_governance import (
    build_overlay_promotion_report,
    detect_overlay_ambiguity,
    validate_overlay_descriptor,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Overlay governance validation gate.")
    parser.add_argument(
        "--overlays-dir",
        type=Path,
        default=Path("overlays"),
        help="Overlay descriptor directory.",
    )
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
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/overlays/overlay_promotion_report.json"),
        help="Output path for overlay promotion report.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    overlays = []
    lint_errors: dict[str, list[dict[str, object]]] = {}

    if args.overlays_dir.exists():
        for path in sorted(args.overlays_dir.glob("*.json")):
            overlay = json.loads(path.read_text(encoding="utf-8"))
            overlays.append(overlay)
            errors = validate_overlay_descriptor(
                overlay,
                schema_dir=args.schema_dir,
                overlay_path=path,
            )
            if errors:
                overlay_id = overlay.get("overlay_id", path.stem)
                lint_errors.setdefault(overlay_id, []).extend(errors)

    ambiguity_errors = detect_overlay_ambiguity(overlays)
    report = build_overlay_promotion_report(
        overlays,
        lint_errors=lint_errors,
        ambiguity_errors=ambiguity_errors,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if lint_errors or ambiguity_errors:
        failure = FailureLabel(
            Type="schema_failure",
            message="Overlay governance validation failed",
            phase_id="validate",
            evidence={
                "lint_errors": lint_errors,
                "ambiguity_errors": ambiguity_errors,
            },
        )
        FailureEmitter(Path("artifacts/failures")).emit(failure, run_id=args.run_id)
        print(f"Overlay governance validation failed: {failure.as_dict()}")
        return 1

    print(f"Overlay governance validation passed: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
