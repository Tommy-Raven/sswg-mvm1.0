from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_cores.cli_arg_parser_core import build_parser, parse_args
from generator.failure_emitter import FailureEmitter, FailureLabel
from generator.hashing import hash_data

from scripts.compatibility_checks import evaluate_compatibility
from scripts.core.overlay_core import (
    OverlayOperationError,
    load_artifact,
    load_overlays,
    write_json,
)


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Compatibility matrix gate for overlays.")
    parser.add_argument(
        "--run-id", type=str, default="compat-matrix", help="Run identifier."
    )
    parser.add_argument(
        "--baseline-artifact",
        type=Path,
        # GOVERNANCE SOURCE REMOVED
        # Canonical governance will be resolved from directive_core/docs/
        default=None,
        help="Baseline artifact path.",
    )
    parser.add_argument(
        "--candidate-artifact",
        type=Path,
        # GOVERNANCE SOURCE REMOVED
        # Canonical governance will be resolved from directive_core/docs/
        default=None,
        help="Candidate artifact path.",
    )
    parser.add_argument(
        "--overlays-dir",
        type=Path,
        default=Path("overlays"),
        help="Overlay descriptor directory.",
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
        "--phase-outputs",
        type=Path,
        # GOVERNANCE SOURCE REMOVED
        # Canonical governance will be resolved from directive_core/docs/
        default=None,
        help="Phase outputs fixture for rollback determinism proof.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=Path("artifacts/compatibility/compatibility_matrix_report.json"),
        help="Output report path.",
    )
    return parse_args(parser)


def _emit_failure(emitter: FailureEmitter, run_id: str, failure: FailureLabel) -> int:
    emitter.emit(failure, run_id=run_id)
    print(f"Compatibility matrix failed: {failure.as_dict()}")
    return 1


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/compatibility/failures"))
    if (
        args.baseline_artifact is None
        or args.candidate_artifact is None
        or args.schema_dir is None
        or args.phase_outputs is None
    ):
        return _emit_failure(
            emitter,
            args.run_id,
            FailureLabel(
                Type="io_failure",
                message="Governance source removed: required paths must be supplied explicitly",
                phase_id="validate",
                evidence={
                    "baseline_artifact": str(args.baseline_artifact),
                    "candidate_artifact": str(args.candidate_artifact),
                    "schema_dir": str(args.schema_dir),
                    "phase_outputs": str(args.phase_outputs),
                },
            ),
        )

    try:
        baseline = load_artifact(args.baseline_artifact)
        candidate = load_artifact(args.candidate_artifact)
        overlays = load_overlays(args.overlays_dir)
    except (OverlayOperationError, OSError, json.JSONDecodeError) as exc:
        return _emit_failure(
            emitter,
            args.run_id,
            FailureLabel(
                Type="schema_failure",
                message=str(exc),
                phase_id="validate",
                evidence={"overlays_dir": str(args.overlays_dir)},
            ),
        )

    compatibility_errors, migration_result, rollback_result = evaluate_compatibility(
        baseline=baseline,
        candidate=candidate,
        overlays=overlays,
        schema_dir=args.schema_dir,
        phase_outputs_path=args.phase_outputs,
        run_id=args.run_id,
    )

    report = {
        "anchor": {
            "anchor_id": "compatibility_matrix_report",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "scripts.compatibility_matrix_gate",
            "status": "draft",
        },
        "run_id": args.run_id,
        "baseline_artifact": str(args.baseline_artifact),
        "candidate_artifact": str(args.candidate_artifact),
        "overlays_dir": str(args.overlays_dir),
        "migration_result": migration_result,
        "rollback_result": rollback_result,
        "compatibility_errors": compatibility_errors,
        "inputs_hash": hash_data(
            {"baseline": baseline, "candidate": candidate, "overlays": overlays}
        ),
    }
    write_json(args.report_path, report)

    if compatibility_errors:
        return _emit_failure(
            emitter,
            args.run_id,
            FailureLabel(
                Type="schema_failure",
                message="Compatibility matrix validation failed",
                phase_id="validate",
                evidence={"report": str(args.report_path)},
            ),
        )

    print(f"Compatibility matrix passed. Report at {args.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
