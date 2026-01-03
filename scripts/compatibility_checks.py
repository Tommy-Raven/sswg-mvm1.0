from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from generator.determinism import replay_determinism_check
from generator.pdl_validator import PDLValidationError, validate_pdl_object

from scripts.overlay_ops import OverlayOperationError, apply_overlays


def evaluate_compatibility(
    *,
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    overlays: list[dict[str, Any]],
    schema_dir: Path,
    phase_outputs_path: Path,
    run_id: str,
) -> tuple[list[dict[str, Any]], str, str]:
    migration_result = "skipped"
    rollback_result = "skipped"
    compatibility_errors: list[dict[str, Any]] = []

    for overlay in overlays:
        compat = overlay.get("compatibility", {})
        status = compat.get("compatibility")
        if status == "backward":
            try:
                migrated = apply_overlays(json.loads(json.dumps(baseline)), [overlay])
                validate_pdl_object(migrated, schema_dir=schema_dir)
                migration_result = "pass"
            except (OverlayOperationError, PDLValidationError) as exc:
                migration_result = "fail"
                compatibility_errors.append(
                    {
                        "overlay_id": overlay.get("overlay_id"),
                        "status": status,
                        "error": str(exc),
                    }
                )
        elif status == "forward":
            try:
                validate_pdl_object(candidate, schema_dir=schema_dir)
            except PDLValidationError as exc:
                compatibility_errors.append(
                    {
                        "overlay_id": overlay.get("overlay_id"),
                        "status": status,
                        "error": exc.label.message,
                    }
                )
        elif status == "breaking":
            migration_plan = compat.get("migration_plan_ref")
            rollback_plan = compat.get("rollback_plan_ref")
            if not migration_plan or not rollback_plan:
                compatibility_errors.append(
                    {
                        "overlay_id": overlay.get("overlay_id"),
                        "status": status,
                        "error": "Missing migration or rollback plan reference",
                    }
                )
                continue
            if not Path(migration_plan).exists() or not Path(rollback_plan).exists():
                compatibility_errors.append(
                    {
                        "overlay_id": overlay.get("overlay_id"),
                        "status": status,
                        "error": "Migration or rollback plan path missing",
                    }
                )
                continue
            try:
                migrated = apply_overlays(json.loads(json.dumps(baseline)), [overlay])
                validate_pdl_object(migrated, schema_dir=schema_dir)
                migration_result = "pass"
            except (OverlayOperationError, PDLValidationError) as exc:
                migration_result = "fail"
                compatibility_errors.append(
                    {
                        "overlay_id": overlay.get("overlay_id"),
                        "status": status,
                        "error": str(exc),
                    }
                )
                continue

            try:
                rollback_payload = json.loads(
                    Path(rollback_plan).read_text(encoding="utf-8")
                )
                rollback_ops = rollback_payload.get("operations", [])
                rolled_back = apply_overlays(
                    json.loads(json.dumps(migrated)), [{"operations": rollback_ops}]
                )
                validate_pdl_object(rolled_back, schema_dir=schema_dir)
                rollback_result = "pass"
            except (
                OverlayOperationError,
                PDLValidationError,
                OSError,
                json.JSONDecodeError,
            ) as exc:
                rollback_result = "fail"
                compatibility_errors.append(
                    {
                        "overlay_id": overlay.get("overlay_id"),
                        "status": status,
                        "error": str(exc),
                    }
                )

            phase_outputs = json.loads(phase_outputs_path.read_text(encoding="utf-8"))
            failure, _ = replay_determinism_check(
                run_id=run_id,
                phase_outputs=phase_outputs,
                required_phases=["normalize", "analyze", "validate", "compare"],
            )
            if failure:
                compatibility_errors.append(
                    {
                        "overlay_id": overlay.get("overlay_id"),
                        "status": status,
                        "error": failure.message,
                        "phase_id": failure.phase_id,
                    }
                )

    return compatibility_errors, migration_result, rollback_result
