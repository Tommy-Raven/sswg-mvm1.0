from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_cores.cli_arg_parser_core import build_parser, parse_args
from generator.failure_emitter import FailureEmitter, FailureLabel
from generator.hashing import hash_data
from generator.pdl_validator import PDLValidationError, validate_pdl_object

from scripts.core.overlay_core import (
    OverlayOperationError,
    apply_overlays,
    load_artifact,
    load_overlays,
    write_json,
)


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Run deterministic migration for overlay compatibility.")
    parser.add_argument(
        "--run-id", type=str, default="migration-run", help="Run identifier."
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        # GOVERNANCE SOURCE REMOVED
        # Canonical governance will be resolved from directive_core/docs/
        default=None,
        help="Artifact path (PDL YAML/JSON) to migrate.",
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
        help="Schema directory for validation.",
    )
    parser.add_argument(
        "--output-artifact",
        type=Path,
        default=Path("artifacts/migrations/migrated_artifact.json"),
        help="Output path for migrated artifact.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=Path("artifacts/migrations/migration_report.json"),
        help="Output path for migration report.",
    )
    return parse_args(parser)


def _emit_failure(emitter: FailureEmitter, run_id: str, failure: FailureLabel) -> int:
    emitter.emit(failure, run_id=run_id)
    print(f"Migration failed: {failure.as_dict()}")
    return 1


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/migrations/failures"))
    if args.artifact is None or args.schema_dir is None:
        return _emit_failure(
            emitter,
            args.run_id,
            FailureLabel(
                Type="io_failure",
                message="Governance source removed: required paths must be supplied explicitly",
                phase_id="validate",
                evidence={
                    "artifact": str(args.artifact),
                    "schema_dir": str(args.schema_dir),
                },
            ),
        )
    try:
        artifact = load_artifact(args.artifact)
        overlays = load_overlays(args.overlays_dir)
        migrated = apply_overlays(json.loads(json.dumps(artifact)), overlays)
    except (OverlayOperationError, json.JSONDecodeError, OSError) as exc:
        return _emit_failure(
            emitter,
            args.run_id,
            FailureLabel(
                Type="schema_failure",
                message=str(exc),
                phase_id="validate",
                evidence={"artifact": str(args.artifact)},
            ),
        )

    try:
        validate_pdl_object(migrated, schema_dir=args.schema_dir)
        validation_result = "pass"
        errors: list[dict[str, Any]] = []
    except PDLValidationError as exc:
        validation_result = "fail"
        errors = exc.label.evidence.get("errors", []) if exc.label.evidence else []

    args.output_artifact.parent.mkdir(parents=True, exist_ok=True)
    args.output_artifact.write_text(json.dumps(migrated, indent=2), encoding="utf-8")

    report = {
        "anchor": {
            "anchor_id": "migration_report",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "scripts.run_migration",
            "status": "draft",
        },
        "run_id": args.run_id,
        "artifact": str(args.artifact),
        "overlays_dir": str(args.overlays_dir),
        "output_artifact": str(args.output_artifact),
        "validation_result": validation_result,
        "errors": errors,
        "inputs_hash": hash_data({"artifact": artifact, "overlays": overlays}),
    }
    write_json(args.report_path, report)

    if validation_result != "pass":
        return _emit_failure(
            emitter,
            args.run_id,
            FailureLabel(
                Type="schema_failure",
                message="Migration validation failed",
                phase_id="validate",
                evidence={"report": str(args.report_path)},
            ),
        )

    print(f"Migration completed. Report at {args.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
