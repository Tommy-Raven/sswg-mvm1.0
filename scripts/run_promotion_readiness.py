from __future__ import annotations

import argparse
import json
from subprocess import run as subprocess_run
import sys
from datetime import datetime, timezone
from pathlib import Path

from ai_evaluation.checkpoints import EvaluationCheckpointer
from cli.cli_arg_parser_core import build_parser, parse_args
from jsonschema import Draft202012Validator
from generator.determinism import (
    bijectivity_check,
    replay_determinism_check,
    write_bijectivity_report,
    write_determinism_report,
)
from generator.autopsy_report import build_autopsy_report, write_autopsy_report
from generator.failure_emitter import (
    FailureEmitter,
    FailureLabel,
    validate_failure_label,
)
from generator.agent_policy import (
    build_policy_manifest,
    detect_working_tree_changes,
    policy_state,
)
from data.outputs.audit_bundle import (
    build_audit_bundle,
    load_audit_spec,
    validate_audit_bundle,
)
from generator.budgeting import (
    collect_artifact_sizes,
    evaluate_budgets,
    load_budget_spec,
)
from generator.pdl_validator import PDLValidationError, validate_pdl_file_with_report
from generator.phase_io import (
    build_phase_io_manifest,
    detect_phase_collapse,
    load_pdl,
    write_manifest,
)
from generator.anchor_registry import AnchorRegistry, enforce_anchor
from generator.environment import check_environment_drift, environment_fingerprint
from generator.evaluation_spec import validate_evaluation_spec
from generator.hashing import hash_data
from generator.invariant_registry import (
    build_coverage_report,
    load_invariants_yaml,
    load_registry,
    validate_registry,
)
from generator.overlay_governance import (
    build_overlay_promotion_report,
    detect_overlay_ambiguity,
    validate_overlay_descriptor,
)
from generator.phase_evidence import (
    build_phase_evidence_bundle,
    write_phase_evidence_bundle,
)
from generator.secret_scanner import load_allowlist, scan_paths
from generator.sanitizer import sanitize_payload


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Run promotion readiness gates.")
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
        "--invariants-path",
        type=Path,
        default=Path("invariants.yaml"),
        help="Invariant declarations path.",
    )
    parser.add_argument(
        "--invariants-registry",
        type=Path,
        default=Path("schemas/invariants_registry.json"),
        help="Invariant registry path.",
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
        "--budget-spec",
        type=Path,
        default=Path("governance/budget_spec.json"),
        help="Budget specification path.",
    )
    parser.add_argument(
        "--allowlist-path",
        type=Path,
        default=Path("governance/secret_allowlist.json"),
        help="Secret allowlist path.",
    )
    parser.add_argument(
        "--audit-spec",
        type=Path,
        default=Path("governance/audit_bundle_spec.json"),
        help="Audit bundle spec path.",
    )
    parser.add_argument(
        "--benchmark-log",
        type=Path,
        default=Path("artifacts/performance/benchmarks_20251227_090721.json"),
        help="Benchmark log path used for audit metrics.",
    )
    parser.add_argument(
        "--repo-mode",
        type=str,
        choices=["qa-readonly", "edit-permitted"],
        default="edit-permitted",
        help="Repository mode for policy enforcement.",
    )
    parser.add_argument(
        "--runbook-path",
        type=Path,
        default=Path("docs/runbook.json"),
        help="Runbook path for docs reproducibility checks.",
    )
    parser.add_argument(
        "--experiment-scope",
        type=Path,
        default=Path("experiments/exp_scope.json"),
        help="Experiment scope declaration path.",
    )
    return parse_args(parser)


def _gate_failure(
    emitter: FailureEmitter,
    run_id: str,
    failure: FailureLabel,
    *,
    autopsy_dir: Path | None = None,
    invariants_registry: dict | None = None,
) -> int:
    if autopsy_dir and invariants_registry is not None:
        report = build_autopsy_report(
            run_id=run_id,
            failure=failure,
            invariants_registry=invariants_registry,
        )
        write_autopsy_report(autopsy_dir / "autopsy_report.json", report)
    emitter.emit(failure, run_id=run_id)
    print(f"Promotion readiness gate failed: {failure.as_dict()}")
    return 1


def _load_metrics(path: Path) -> dict[str, float]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {name: float(value) for name, value in payload.get("metrics", {}).items()}


def _has_breaking_override(overlays: list[dict]) -> bool:
    for overlay in overlays:
        compatibility = overlay.get("compatibility", {})
        if compatibility.get("compatibility") == "breaking":
            if all(
                compatibility.get(key)
                for key in ("migration_plan_ref", "rollback_plan_ref")
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
    repo_root = Path(".")
    root_agents = repo_root / "AGENTS.md"
    if not root_agents.exists():
        return _gate_failure(
            failure_emitter,
            args.run_id,
            FailureLabel(
                Type="tool_mismatch",
                message="Root AGENTS.md missing from repository",
                phase_id="validate",
                evidence={"path": str(root_agents)},
            ),
        )
    if args.repo_mode == "qa-readonly":
        changes = detect_working_tree_changes(repo_root)
        if changes:
            return _gate_failure(
                failure_emitter,
                args.run_id,
                FailureLabel(
                    Type="tool_mismatch",
                    message="QA mode forbids working tree modifications",
                    phase_id="validate",
                    evidence={"changes": changes},
                ),
            )
    policy = policy_state(repo_root, args.repo_mode)
    policy_manifest = build_policy_manifest(policy, effective_scope=root_agents)
    policy_manifest_path = Path("artifacts/policy/policy_manifest.json")
    policy_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    policy_manifest_path.write_text(
        json.dumps(policy_manifest, indent=2), encoding="utf-8"
    )

    if not args.invariants_path.exists():
        return _gate_failure(
            failure_emitter,
            args.run_id,
            FailureLabel(
                Type="io_failure",
                message="Invariant declarations missing",
                phase_id="validate",
                evidence={"path": str(args.invariants_path)},
            ),
        )
    if not args.invariants_registry.exists():
        return _gate_failure(
            failure_emitter,
            args.run_id,
            FailureLabel(
                Type="io_failure",
                message="Invariant registry missing",
                phase_id="validate",
                evidence={"path": str(args.invariants_registry)},
            ),
        )

    declared_invariants = load_invariants_yaml(args.invariants_path)
    invariants_registry = load_registry(args.invariants_registry)
    registry_errors = validate_registry(invariants_registry)
    if registry_errors:
        return _gate_failure(
            failure_emitter,
            args.run_id,
            FailureLabel(
                Type="schema_failure",
                message="Invariant registry validation failed",
                phase_id="validate",
                evidence={"errors": registry_errors},
            ),
            autopsy_dir=evidence_dir,
            invariants_registry=invariants_registry,
        )

    coverage_report = build_coverage_report(
        declared_invariants=declared_invariants,
        registry_payload=invariants_registry,
        repo_root=repo_root,
    )
    invariant_coverage_path = evidence_dir / "invariant_coverage_report.json"
    invariant_coverage_path.write_text(
        json.dumps(coverage_report, indent=2), encoding="utf-8"
    )
    if coverage_report.get("status") != "pass":
        missing_ids = [
            entry.get("id") for entry in coverage_report.get("missing_enforcement", [])
        ]
        return _gate_failure(
            failure_emitter,
            args.run_id,
            FailureLabel(
                Type="schema_failure",
                message="Invariant enforcement coverage failed",
                phase_id="validate",
                evidence={
                    "missing_registry": coverage_report.get("missing_registry", []),
                    "missing_enforcement": coverage_report.get(
                        "missing_enforcement", []
                    ),
                    "invariant_ids": [item for item in missing_ids if item],
                },
            ),
            autopsy_dir=evidence_dir,
            invariants_registry=invariants_registry,
        )

    def gate_failure(failure: FailureLabel) -> int:
        return _gate_failure(
            failure_emitter,
            args.run_id,
            failure,
            autopsy_dir=evidence_dir,
            invariants_registry=invariants_registry,
        )

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
        return gate_failure(failure)

    validation_reports = list(
        (evidence_dir / "validation").glob("pdl_validation_*.json")
    )
    if validation_reports:
        report_path = validation_reports[0]
        report_payload = json.loads(report_path.read_text(encoding="utf-8"))
        anchor_failure = enforce_anchor(
            artifact_path=report_path,
            metadata=report_payload.get("anchor", {}),
            registry=AnchorRegistry(args.anchor_registry),
        )
        if anchor_failure:
            return gate_failure(anchor_failure)

    pdl_obj = load_pdl(args.pdl_path)
    observed = json.loads(args.observed_io.read_text(encoding="utf-8"))
    manifest = build_phase_io_manifest(pdl_obj, observed)
    collapse = detect_phase_collapse(manifest, pdl_obj)
    if collapse:
        return gate_failure(collapse)
    write_manifest(evidence_dir / "phase_io_manifest.json", manifest)

    phase_outputs = json.loads(args.phase_outputs.read_text(encoding="utf-8"))
    failure, determinism_report = replay_determinism_check(
        run_id=args.run_id,
        phase_outputs=phase_outputs,
        required_phases=["normalize", "analyze", "validate", "compare"],
    )
    write_determinism_report(
        evidence_dir / "determinism_report.json", determinism_report
    )
    if failure:
        return gate_failure(failure)
    measurement_ids = json.loads(args.measurement_ids.read_text(encoding="utf-8"))
    id_failure = bijectivity_check(measurement_ids.get("ids", []))
    write_bijectivity_report(
        evidence_dir / "bijectivity_report.json",
        measurement_ids.get("ids", []),
        id_failure,
    )
    if id_failure:
        return gate_failure(id_failure)

    phase_evidence_bundle = build_phase_evidence_bundle(
        run_id=args.run_id,
        pdl_obj=pdl_obj,
        observed_io=observed,
        phase_outputs=phase_outputs,
        invariants_registry=invariants_registry,
    )
    phase_evidence_path = evidence_dir / "phase_evidence_bundle.json"
    write_phase_evidence_bundle(phase_evidence_path, phase_evidence_bundle)

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
    for overlay_path in (
        sorted(args.overlays_dir.glob("*.json")) if args.overlays_dir.exists() else []
    ):
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
    overlay_report_path.write_text(
        json.dumps(overlay_report, indent=2), encoding="utf-8"
    )

    if overlay_lint_errors or ambiguity_errors:
        return gate_failure(
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
                    return gate_failure(
                        FailureLabel(
                            Type="schema_failure",
                            message="Experimental overlays cannot target global scope without explicit approval",
                            phase_id="validate",
                            evidence={"overlay_id": overlay.get("overlay_id")},
                        ),
                    )
        if not args.experiment_scope.exists():
            return gate_failure(
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
                json.loads(
                    (args.schema_dir / "experiment-scope.json").read_text(
                        encoding="utf-8"
                    )
                )
            ).iter_errors(exp_scope),
            key=lambda e: e.path,
        )
        if exp_errors:
            return gate_failure(
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
            return gate_failure(
                FailureLabel(
                    Type="schema_failure",
                    message="Experiment scope exit criteria not met for graduation",
                    phase_id="validate",
                    evidence={"exp_id": exp_scope.get("exp_id")},
                ),
            )

    if not args.eval_spec.exists():
        return gate_failure(
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
        return gate_failure(
            FailureLabel(
                Type="schema_failure",
                message="Evaluation spec validation failed",
                phase_id="validate",
                evidence={"errors": eval_errors},
            ),
        )
    rollback_artifact = eval_spec.get("rollback_plan", {}).get("artifact")
    if rollback_artifact and not Path(rollback_artifact).exists():
        return gate_failure(
            FailureLabel(
                Type="reproducibility_failure",
                message="Evaluation rollback plan artifact is missing",
                phase_id="validate",
                evidence={"path": rollback_artifact},
            ),
        )

    criteria = {
        metric["name"]: metric["threshold"] for metric in eval_spec.get("metrics", [])
    }
    tolerance = float(eval_spec.get("regression_definition", {}).get("tolerance", 0.0))
    checkpointer = EvaluationCheckpointer(
        success_criteria=criteria, tolerance=tolerance
    )
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
        "inputs_hash": hash_data(
            {"baseline": baseline_metrics, "candidate": candidate_metrics}
        ),
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
        return gate_failure(
            FailureLabel(
                Type="reproducibility_failure",
                message="Evaluation checkpoint failed",
                phase_id="validate",
                evidence={"report": str(eval_report_path)},
            ),
        )

    env_failure = check_environment_drift(args.lock_path)
    if env_failure:
        return gate_failure(env_failure)

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
            "invariant_coverage": coverage_report.get("status", "pass"),
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
        compare_output_path.write_text(
            json.dumps(compare_output, indent=2), encoding="utf-8"
        )

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
        invariant_coverage_path,
        phase_evidence_path,
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
    provenance_path.write_text(
        json.dumps(provenance_manifest, indent=2), encoding="utf-8"
    )

    provenance_target = Path("artifacts/provenance/provenance_manifest.json")
    provenance_target.parent.mkdir(parents=True, exist_ok=True)
    provenance_target.write_text(
        json.dumps(provenance_manifest, indent=2), encoding="utf-8"
    )

    if not args.budget_spec.exists():
        return gate_failure(
            FailureLabel(
                Type="reproducibility_failure",
                message="Budget specification missing",
                phase_id="validate",
                evidence={"path": str(args.budget_spec)},
            ),
        )
    budget_spec = load_budget_spec(args.budget_spec)
    telemetry_payload = {
        "anchor": {
            "anchor_id": "run_telemetry",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "scripts.run_promotion_readiness",
            "status": "draft",
        },
        "run_id": args.run_id,
        "phase_durations": {
            phase: 0.0
            for phase in [
                "ingest",
                "normalize",
                "parse",
                "analyze",
                "generate",
                "validate",
                "compare",
                "interpret",
                "log",
            ]
        },
        "artifact_sizes": [],
        "budget_status": {
            "status": "pass",
            "phase_budgets": {},
            "artifact_budgets": {},
            "total_budget": "pass",
        },
        "gate_results": env_report.get("phase_status", {}),
        "failure_counts": {
            "deterministic_failure": 0,
            "schema_failure": 0,
            "io_failure": 0,
            "tool_mismatch": 0,
            "reproducibility_failure": 0,
        },
        "determinism_status": {
            phase: "pass" for phase in ["normalize", "analyze", "validate", "compare"]
        },
        "overlay_chain": [
            {
                "overlay_id": overlay.get("overlay_id"),
                "overlay_version": overlay.get("overlay_version"),
            }
            for overlay in overlays
        ],
        "inputs_hash": hash_data({"pdl": pdl_obj, "overlays": overlays}),
        "emitted_at": datetime.now(timezone.utc).isoformat(),
    }
    telemetry_path = Path("artifacts/telemetry/run_telemetry.json")
    telemetry_path.parent.mkdir(parents=True, exist_ok=True)
    telemetry_path.write_text(
        json.dumps(sanitize_payload(telemetry_payload), indent=2),
        encoding="utf-8",
    )

    artifact_sizes = collect_artifact_sizes(budget_spec.get("artifact_budgets", []))
    budget_report = evaluate_budgets(
        budget_spec=budget_spec,
        phase_durations=telemetry_payload["phase_durations"],
        artifact_sizes=artifact_sizes,
    )
    budget_report_payload = {
        "anchor": {
            "anchor_id": "budget_report",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "scripts.run_promotion_readiness",
            "status": "draft",
        },
        "run_id": args.run_id,
        **budget_report,
    }
    budget_report_path = Path("artifacts/budgets/budget_report.json")
    budget_report_path.parent.mkdir(parents=True, exist_ok=True)
    budget_report_path.write_text(
        json.dumps(budget_report_payload, indent=2), encoding="utf-8"
    )
    if budget_report_payload.get("status") != "pass":
        return gate_failure(
            FailureLabel(
                Type="reproducibility_failure",
                message="Budget validation failed",
                phase_id="validate",
                evidence={"violations": budget_report_payload.get("violations", [])},
            ),
        )

    telemetry_payload["artifact_sizes"] = [
        {
            "artifact_class": entry.get("artifact_class"),
            "paths": entry.get("paths", []),
            "size_bytes": entry.get("size_bytes", 0),
            "max_size_bytes": entry.get("max_size_bytes", 0),
            "pass": entry.get("pass", False),
        }
        for entry in budget_report_payload.get("artifact_results", [])
    ]
    telemetry_payload["budget_status"] = {
        "status": budget_report_payload.get("status"),
        "phase_budgets": {
            entry.get("phase"): "pass" if entry.get("pass") else "fail"
            for entry in budget_report_payload.get("phase_results", [])
        },
        "artifact_budgets": {
            entry.get("artifact_class"): "pass" if entry.get("pass") else "fail"
            for entry in budget_report_payload.get("artifact_results", [])
        },
        "total_budget": (
            "pass"
            if budget_report_payload.get("total_duration_sec", 0)
            <= budget_report_payload.get("max_total_duration_sec", 0)
            else "fail"
        ),
    }
    telemetry_path.write_text(
        json.dumps(sanitize_payload(telemetry_payload), indent=2),
        encoding="utf-8",
    )

    docs_proc = subprocess_run(  # nosec B603
        [
            sys.executable,
            "scripts/docs_repro_check.py",
            "--runbook-path",
            str(args.runbook_path),
            "--run-id",
            args.run_id,
        ],
        check=False,
    )
    if docs_proc.returncode != 0:
        return gate_failure(
            FailureLabel(
                Type="reproducibility_failure",
                message="Docs reproducibility check failed",
                phase_id="validate",
                evidence={"runbook_path": str(args.runbook_path)},
            ),
        )

    if not args.audit_spec.exists():
        return gate_failure(
            FailureLabel(
                Type="reproducibility_failure",
                message="Audit bundle spec missing",
                phase_id="validate",
                evidence={"path": str(args.audit_spec)},
            ),
        )
    if not args.benchmark_log.exists():
        return gate_failure(
            FailureLabel(
                Type="reproducibility_failure",
                message="Benchmark log missing",
                phase_id="validate",
                evidence={"path": str(args.benchmark_log)},
            ),
        )
    audit_spec = load_audit_spec(args.audit_spec)
    audit_manifest_path = Path("artifacts/audit/audit_bundle_manifest.json")
    audit_manifest = build_audit_bundle(
        spec=audit_spec,
        run_id=args.run_id,
        bundle_dir=Path("artifacts/audit") / args.run_id,
        manifest_path=audit_manifest_path,
        benchmark_log_path=args.benchmark_log,
    )
    audit_validation = validate_audit_bundle(audit_manifest)
    if audit_validation["status"] != "pass":
        return gate_failure(
            FailureLabel(
                Type="reproducibility_failure",
                message="Audit bundle validation failed",
                phase_id="validate",
                evidence={"errors": audit_validation.get("errors", [])},
            ),
        )
    audit_certificate = {
        "anchor": {
            "anchor_id": "audit_certificate",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "scripts.run_promotion_readiness",
            "status": "draft",
        },
        "run_id": args.run_id,
        "bundle_hash": audit_manifest.get("bundle_hash"),
        "coverage": {
            "bundle_complete": True,
            "hash_integrity": True,
            "consistency_checks": True,
        },
        "gating_summary": {
            "audit_readiness_validation": "pass",
        },
    }
    audit_certificate_path = Path("artifacts/audit/audit_certificate.json")
    audit_certificate_path.write_text(
        json.dumps(audit_certificate, indent=2), encoding="utf-8"
    )

    allowlist = load_allowlist(args.allowlist_path)
    secret_scan = scan_paths(
        [
            Path("artifacts"),
            Path("data"),
            Path("docs"),
            Path("overlays"),
            Path("config/anchor_registry.json"),
        ],
        allowlist=allowlist,
    )
    if secret_scan["violations"] or secret_scan["allowlist_errors"]:
        return gate_failure(
            FailureLabel(
                Type="reproducibility_failure",
                message="Secret scanning gate detected sensitive content",
                phase_id="validate",
                evidence=secret_scan,
            ),
        )

    for path in [
        overlay_manifest_path,
        overlay_report_path,
        eval_report_path,
        variance_path,
        log_report_path,
        telemetry_path,
        budget_report_path,
        policy_manifest_path,
        audit_manifest_path,
        audit_certificate_path,
        provenance_path,
    ]:
        anchor_failure = enforce_anchor(
            artifact_path=path,
            metadata=json.loads(path.read_text(encoding="utf-8")).get("anchor", {}),
            registry=registry,
        )
        if anchor_failure:
            return gate_failure(anchor_failure)
    if compare_output_path:
        compare_anchor_failure = enforce_anchor(
            artifact_path=compare_output_path,
            metadata=json.loads(compare_output_path.read_text(encoding="utf-8")).get(
                "anchor", {}
            ),
            registry=registry,
        )
        if compare_anchor_failure:
            return gate_failure(compare_anchor_failure)

    try:
        validate_failure_label(
            FailureLabel(
                Type="schema_failure",
                message="Failure label validation check",
                phase_id="validate",
            )
        )
    except ValueError as exc:
        return gate_failure(
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
