from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_evaluation.checkpoints import EvaluationCheckpointer
from jsonschema import Draft202012Validator
from generator.determinism import (
    bijectivity_check,
    replay_determinism_check,
    write_bijectivity_report,
    write_determinism_report,
)
from generator.failure_emitter import FailureEmitter, FailureLabel, validate_failure_label
from generator.pdl_validator import PDLValidationError, validate_pdl_file_with_report
from generator.phase_io import build_phase_io_manifest, detect_phase_collapse, load_pdl, write_manifest
from generator.anchor_registry import AnchorRegistry, enforce_anchor
from generator.environment import check_environment_drift, environment_fingerprint
from generator.evaluation_spec import validate_evaluation_spec
from generator.hashing import hash_data
from generator.overlay_governance import (
    build_overlay_promotion_report,
    detect_overlay_ambiguity,
    validate_overlay_descriptor,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run promotion readiness gates.")
    parser.add_argument(
        "--run-id",
        type=str,
        default="local-run",
        help="Run identifier.",
    )
    parser.add_argument(
        "--pdl-path",
        type=Path,
        default=Path("pdl/example_full_9_phase.yaml"),
        help="PDL path to validate.",
    )
    parser.add_argument(
        "--schema-dir",
        type=Path,
        default=Path("schemas"),
        help="Schema directory.",
    )
    parser.add_argument(
        "--phase-outputs",
        type=Path,
        default=Path("tests/fixtures/phase_outputs.json"),
        help="Phase outputs fixture for determinism replay.",
    )
    parser.add_argument(
        "--measurement-ids",
        type=Path,
        default=Path("tests/fixtures/measurement_ids.json"),
        help="Measurement identifiers fixture.",
    )
    parser.add_argument(
        "--observed-io",
        type=Path,
        default=Path("tests/fixtures/observed_io.json"),
        help="Observed IO fixture for phase IO manifest.",
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=Path("artifacts/evidence_pack"),
        help="Evidence pack output directory.",
    )
    parser.add_argument(
        "--eval-spec",
        type=Path,
        default=Path("evaluations/eval_spec.json"),
        help="Evaluation spec path.",
    )
    parser.add_argument(
        "--eval-baseline",
        type=Path,
        default=Path("tests/fixtures/eval_baseline.json"),
        help="Baseline evaluation metrics JSON.",
    )
    parser.add_argument(
        "--eval-candidate",
        type=Path,
        default=Path("tests/fixtures/eval_candidate.json"),
        help="Candidate evaluation metrics JSON.",
    )
    parser.add_argument(
        "--anchor-registry",
        type=Path,
        default=Path("config/anchor_registry.json"),
        help="Anchor registry path.",
    )
    parser.add_argument(
        "--overlays-dir",
        type=Path,
        default=Path("overlays"),
        help="Overlay descriptor directory.",
    )
    parser.add_argument(
        "--lock-path",
        type=Path,
        default=Path("reproducibility/dependency_lock.json"),
        help="Dependency lock path.",
    )
    parser.add_argument(
        "--release-track",
        type=str,
        default="sswg",
        choices=["sswg", "sswg-exp", "sswg-trs"],
        help="Release track for promotion gating.",
    )
    parser.add_argument(
        "--experiment-scope",
        type=Path,
        default=Path("experiments/exp_scope.json"),
        help="Experiment scope declaration path.",
    )
    return parser.parse_args()


def _gate_failure(emitter: FailureEmitter, run_id: str, failure: FailureLabel) -> int:
    emitter.emit(failure, run_id=run_id)
    print(f"Promotion readiness gate failed: {failure.as_dict()}")
    return 1


def _load_metrics(path: Path) -> dict[str, float]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {name: float(value) for name, value in payload.get("metrics", {}).items()}


def _has_breaking_override(overlays: list[dict]) -> bool:
    for overlay in overlays:
        compatibility = overlay.get("compatibility", {})
        if compatibility.get("status") == "breaking":
            if all(
                compatibility.get(key)
                for key in ("migration_plan", "migration_steps", "rollback_plan")
            ):
                return True
    return False


def _collect_artifact_entry(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "path": str(path),
        "hash": hash_data(payload),
        "anchor": payload.get("anchor", {}),
    }


def main() -> int:
    args = _parse_args()
    evidence_dir = args.evidence_dir / args.run_id
    evidence_dir.mkdir(parents=True, exist_ok=True)
    failure_emitter = FailureEmitter(evidence_dir / "failures")

    try:
        validate_pdl_file_with_report(
            pdl_path=args.pdl_path,
            schema_dir=args.schema_dir,
            report_dir=evidence_dir / "validation",
            run_id=args.run_id,
        )
    except PDLValidationError as exc:
        failure = FailureLabel(
            Type=exc.label.Type,
            message=exc.label.message,
            phase_id="validate",
            evidence=exc.label.evidence,
        )
        return _gate_failure(failure_emitter, args.run_id, failure)

    validation_reports = list((evidence_dir / "validation").glob("pdl_validation_*.json"))
    if validation_reports:
        report_path = validation_reports[0]
        report_payload = json.loads(report_path.read_text(encoding="utf-8"))
        anchor_failure = enforce_anchor(
            artifact_path=report_path,
            metadata=report_payload.get("anchor", {}),
            registry=AnchorRegistry(args.anchor_registry),
        )
        if anchor_failure:
            return _gate_failure(failure_emitter, args.run_id, anchor_failure)

    pdl_obj = load_pdl(args.pdl_path)
    observed = json.loads(args.observed_io.read_text(encoding="utf-8"))
    manifest = build_phase_io_manifest(pdl_obj, observed)
    collapse = detect_phase_collapse(manifest, pdl_obj)
    if collapse:
        return _gate_failure(failure_emitter, args.run_id, collapse)
    write_manifest(evidence_dir / "phase_io_manifest.json", manifest)

    phase_outputs = json.loads(args.phase_outputs.read_text(encoding="utf-8"))
    failure, report = replay_determinism_check(
        run_id=args.run_id,
        phase_outputs=phase_outputs,
        required_phases=["normalize", "analyze", "validate", "compare"],
    )
    write_determinism_report(evidence_dir / "determinism_report.json", report)
    if failure:
        return _gate_failure(failure_emitter, args.run_id, failure)
    measurement_ids = json.loads(args.measurement_ids.read_text(encoding="utf-8"))
    id_failure = bijectivity_check(measurement_ids.get("ids", []))
    write_bijectivity_report(
        evidence_dir / "bijectivity_report.json",
        measurement_ids.get("ids", []),
        id_failure,
    )
    if id_failure:
        return _gate_failure(failure_emitter, args.run_id, id_failure)

    registry = AnchorRegistry(args.anchor_registry)
    registry_data = registry.load()
    overlays: list[dict] = []
    if args.overlays_dir.exists():
        overlays = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(args.overlays_dir.glob("*.json"))
        ]
    overlay_payload = {
        "anchor": {
            "anchor_id": "overlay_chain_manifest",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "scripts.run_promotion_readiness",
            "status": "draft",
        },
        "run_id": args.run_id,
        "registry_snapshot": registry_data,
        "overlays": overlays,
    }
    overlay_payload["inputs_hash"] = hash_data(overlay_payload)
    overlay_manifest_path = evidence_dir / "overlay_chain_manifest.json"
    overlay_manifest_path.write_text(
        json.dumps(overlay_payload, indent=2),
        encoding="utf-8",
    )

    overlay_lint_errors: dict[str, list[dict[str, object]]] = {}
    for overlay_path in sorted(args.overlays_dir.glob("*.json")) if args.overlays_dir.exists() else []:
        overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
        errors = validate_overlay_descriptor(
            overlay,
            schema_dir=args.schema_dir,
            overlay_path=overlay_path,
        )
        if errors:
            overlay_id = overlay.get("overlay_id", overlay_path.stem)
            overlay_lint_errors.setdefault(overlay_id, []).extend(errors)

    ambiguity_errors = detect_overlay_ambiguity(overlays)
    overlay_report = build_overlay_promotion_report(
        overlays,
        lint_errors=overlay_lint_errors,
        ambiguity_errors=ambiguity_errors,
    )
    overlay_report_path = evidence_dir / "overlay_promotion_report.json"
    overlay_report_path.write_text(json.dumps(overlay_report, indent=2), encoding="utf-8")

    if overlay_lint_errors or ambiguity_errors:
        return _gate_failure(
            failure_emitter,
            args.run_id,
            FailureLabel(
                Type="schema_failure",
                message="Overlay governance validation failed",
                phase_id="validate",
                evidence={
                    "lint_errors": overlay_lint_errors,
                    "ambiguity_errors": ambiguity_errors,
                },
            ),
        )

    if args.release_track == "sswg-exp":
        global_overrides = [
            overlay
            for overlay in overlays
            if overlay.get("precedence", {}).get("scope") == "global"
        ]
        if global_overrides:
            for overlay in global_overrides:
                notes = overlay.get("precedence", {}).get("notes", "")
                if "exp-approved" not in notes.lower():
                    return _gate_failure(
                        failure_emitter,
                        args.run_id,
                        FailureLabel(
                            Type="schema_failure",
                            message="Experimental overlays cannot target global scope without explicit approval",
                            phase_id="validate",
                            evidence={"overlay_id": overlay.get("overlay_id")},
                        ),
                    )
        if not args.experiment_scope.exists():
            return _gate_failure(
                failure_emitter,
                args.run_id,
                FailureLabel(
                    Type="schema_failure",
                    message="Experiment scope declaration missing",
                    phase_id="validate",
                    evidence={"path": str(args.experiment_scope)},
                ),
            )
        exp_scope = json.loads(args.experiment_scope.read_text(encoding="utf-8"))
        exp_errors = sorted(
            Draft202012Validator(
                json.loads((args.schema_dir / "experiment-scope.json").read_text(encoding="utf-8"))
            ).iter_errors(exp_scope),
            key=lambda e: e.path,
        )
        if exp_errors:
            return _gate_failure(
                failure_emitter,
                args.run_id,
                FailureLabel(
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
                            for error in exp_errors
                        ]
                    },
                ),
            )
        if not exp_scope.get("graduation_ready"):
            return _gate_failure(
                failure_emitter,
                args.run_id,
                FailureLabel(
                    Type="schema_failure",
                    message="Experiment scope exit criteria not met for graduation",
                    phase_id="validate",
                    evidence={"exp_id": exp_scope.get("exp_id")},
                ),
            )

    if not args.eval_spec.exists():
        return _gate_failure(
            failure_emitter,
            args.run_id,
            FailureLabel(
                Type="reproducibility_failure",
                message="Evaluation spec is missing",
                phase_id="validate",
                evidence={"path": str(args.eval_spec)},
            ),
        )

    eval_spec = json.loads(args.eval_spec.read_text(encoding="utf-8"))
    eval_errors = validate_evaluation_spec(
        eval_spec,
        schema_dir=args.schema_dir,
        spec_path=args.eval_spec,
    )
    if eval_errors:
        return _gate_failure(
            failure_emitter,
            args.run_id,
            FailureLabel(
                Type="schema_failure",
                message="Evaluation spec validation failed",
                phase_id="validate",
                evidence={"errors": eval_errors},
            ),
        )
    rollback_artifact = eval_spec.get("rollback_plan", {}).get("artifact")
    if rollback_artifact and not Path(rollback_artifact).exists():
        return _gate_failure(
            failure_emitter,
            args.run_id,
            FailureLabel(
                Type="reproducibility_failure",
                message="Evaluation rollback plan artifact is missing",
                phase_id="validate",
                evidence={"path": rollback_artifact},
            ),
        )

    criteria = {metric["name"]: metric["threshold"] for metric in eval_spec.get("metrics", [])}
    tolerance = float(eval_spec.get("regression_definition", {}).get("tolerance", 0.0))
    checkpointer = EvaluationCheckpointer(success_criteria=criteria, tolerance=tolerance)
    baseline_metrics = _load_metrics(args.eval_baseline)
    candidate_metrics = _load_metrics(args.eval_candidate)
    checkpointer.record("baseline", baseline_metrics)
    candidate_checkpoint = checkpointer.record("candidate", candidate_metrics)
    deltas = {
        name: candidate_metrics.get(name, 0.0) - baseline_metrics.get(name, 0.0)
        for name in set(baseline_metrics) | set(candidate_metrics)
    }
    override_used = False
    if not candidate_checkpoint.passed and _has_breaking_override(overlays):
        override_used = True

    eval_report = {
        "anchor": {
            "anchor_id": "evaluation_report",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "scripts.run_promotion_readiness",
            "status": "draft",
        },
        "run_id": args.run_id,
        "eval_id": eval_spec.get("eval_id"),
        "eval_version": eval_spec.get("eval_version"),
        "baseline": baseline_metrics,
        "candidate": candidate_metrics,
        "deltas": deltas,
        "passed": candidate_checkpoint.passed,
        "regressions": candidate_checkpoint.regressions,
        "rollback_recommended": candidate_checkpoint.rollback_recommended,
        "override_used": override_used,
        "inputs_hash": hash_data({"baseline": baseline_metrics, "candidate": candidate_metrics}),
    }
    eval_report_path = evidence_dir / "eval_report.json"
    eval_report_path.write_text(json.dumps(eval_report, indent=2), encoding="utf-8")

    interpret_notes = json.loads(args.eval_candidate.read_text(encoding="utf-8")).get(
        "interpretive_notes", []
    )
    variance_payload = {
        "anchor": {
            "anchor_id": "interpret_variance_notes",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "scripts.run_promotion_readiness",
            "status": "draft",
        },
        "run_id": args.run_id,
        "notes": interpret_notes,
    }
    variance_path = evidence_dir / "interpret_variance_notes.json"
    variance_path.write_text(json.dumps(variance_payload, indent=2), encoding="utf-8")

    if not candidate_checkpoint.passed and not override_used:
        return _gate_failure(
            failure_emitter,
            args.run_id,
            FailureLabel(
                Type="reproducibility_failure",
                message="Evaluation checkpoint failed",
                phase_id="validate",
                evidence={"report": str(eval_report_path)},
            ),
        )

    env_failure = check_environment_drift(args.lock_path)
    if env_failure:
        return _gate_failure(failure_emitter, args.run_id, env_failure)

    env_report = {
        "anchor": {
            "anchor_id": "log_phase_report",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "scripts.run_promotion_readiness",
            "status": "draft",
        },
        "run_id": args.run_id,
        "inputs_hash": hash_data({"pdl": pdl_obj, "overlays": overlays}),
        "phase_status": {
            "schema_validation": "pass",
            "phase_schema_validation": "pass",
            "invariants_validation": "pass",
            "reproducibility_validation": "pass",
        },
        "environment": environment_fingerprint(args.lock_path),
    }
    log_report_path = evidence_dir / "log_phase_report.json"
    log_report_path.write_text(json.dumps(env_report, indent=2), encoding="utf-8")

    compare_output_path = None
    if "compare" in phase_outputs:
        compare_output = {
            "anchor": {
                "anchor_id": "compare_output",
                "anchor_version": "1.0.0",
                "scope": "run",
                "owner": "scripts.run_promotion_readiness",
                "status": "draft",
            },
            "run_id": args.run_id,
            "output": phase_outputs.get("compare"),
        }
        compare_output_path = evidence_dir / "compare_output.json"
        compare_output_path.write_text(json.dumps(compare_output, indent=2), encoding="utf-8")

    if args.release_track == "sswg-exp":
        exp_summary = {
            "anchor": {
                "anchor_id": "experiment_summary",
                "anchor_version": "1.0.0",
                "scope": "run",
                "owner": "scripts.run_promotion_readiness",
                "status": "draft",
            },
            "run_id": args.run_id,
            "eval_report": str(eval_report_path),
            "provenance_manifest": str(evidence_dir / "provenance_manifest.json"),
            "determinism_report": str(evidence_dir / "determinism_report.json"),
            "notes": "sswg-exp run results pack generated.",
        }
        (evidence_dir / "experiment_summary.json").write_text(
            json.dumps(exp_summary, indent=2),
            encoding="utf-8",
        )

    artifact_paths = [
        overlay_manifest_path,
        overlay_report_path,
        eval_report_path,
        variance_path,
        log_report_path,
        evidence_dir / "determinism_report.json",
        evidence_dir / "bijectivity_report.json",
        evidence_dir / "phase_io_manifest.json",
    ]
    if compare_output_path:
        artifact_paths.append(compare_output_path)

    schema_refs = []
    for schema_path in sorted(args.schema_dir.glob("*.json")):
        schema_payload = json.loads(schema_path.read_text(encoding="utf-8"))
        schema_refs.append(
            {
                "schema_id": schema_payload.get("$id", str(schema_path)),
                "content_hash": hash_data(schema_payload),
            }
        )

    phase_handlers = [
        {"phase": phase.get("name"), "handler": phase.get("handler")}
        for phase in pdl_obj.get("phases", [])
    ]
    provenance_manifest = {
        "anchor": {
            "anchor_id": "provenance_manifest",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "scripts.run_promotion_readiness",
            "status": "draft",
        },
        "run_id": args.run_id,
        "inputs_hash": hash_data({"pdl": pdl_obj, "overlays": overlays}),
        "pdl_ref": str(args.pdl_path),
        "schema_refs": schema_refs,
        "overlay_chain": [
            {
                "overlay_id": overlay.get("overlay_id"),
                "overlay_version": overlay.get("overlay_version"),
            }
            for overlay in overlays
        ],
        "phase_handlers": phase_handlers,
        "artifacts": [_collect_artifact_entry(path) for path in artifact_paths],
    }
    provenance_path = evidence_dir / "provenance_manifest.json"
    provenance_path.write_text(json.dumps(provenance_manifest, indent=2), encoding="utf-8")

    provenance_target = Path("artifacts/provenance/provenance_manifest.json")
    provenance_target.parent.mkdir(parents=True, exist_ok=True)
    provenance_target.write_text(json.dumps(provenance_manifest, indent=2), encoding="utf-8")

    for path in [
        overlay_manifest_path,
        overlay_report_path,
        eval_report_path,
        variance_path,
        log_report_path,
        provenance_path,
    ]:
        anchor_failure = enforce_anchor(
            artifact_path=path,
            metadata=json.loads(path.read_text(encoding="utf-8")).get("anchor", {}),
            registry=registry,
        )
        if anchor_failure:
            return _gate_failure(failure_emitter, args.run_id, anchor_failure)
    if compare_output_path:
        compare_anchor_failure = enforce_anchor(
            artifact_path=compare_output_path,
            metadata=json.loads(compare_output_path.read_text(encoding="utf-8")).get("anchor", {}),
            registry=registry,
        )
        if compare_anchor_failure:
            return _gate_failure(failure_emitter, args.run_id, compare_anchor_failure)

    try:
        validate_failure_label(
            FailureLabel(
                Type="schema_failure",
                message="Failure label validation check",
                phase_id="validate",
            )
        )
    except ValueError as exc:
        return _gate_failure(
            failure_emitter,
            args.run_id,
            FailureLabel(
                Type="tool_mismatch",
                message=str(exc),
                phase_id="validate",
            ),
        )

    print(f"Promotion readiness gates passed. Evidence at {evidence_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
