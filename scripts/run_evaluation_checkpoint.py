from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from ai_evaluation.checkpoints import EvaluationCheckpointer
from generator.evaluation_spec import validate_evaluation_spec
from generator.failure_emitter import FailureEmitter, FailureLabel
from generator.hashing import hash_data


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run evaluation checkpoint gate.")
    parser.add_argument(
        "--eval-spec",
        type=Path,
        default=Path("evaluations/eval_spec.json"),
        help="Evaluation spec path.",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=Path("tests/fixtures/eval_baseline.json"),
        help="Baseline metrics JSON.",
    )
    parser.add_argument(
        "--candidate",
        type=Path,
        default=Path("tests/fixtures/eval_candidate.json"),
        help="Candidate metrics JSON.",
    )
    parser.add_argument(
        "--schema-dir",
        type=Path,
        default=Path("schemas"),
        help="Schema directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/evaluation"),
        help="Output directory for evaluation artifacts.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="local-run",
        help="Run identifier.",
    )
    parser.add_argument(
        "--allow-breaking-override",
        action="store_true",
        help="Allow breaking overlay override for regressions.",
    )
    return parser.parse_args()


def _load_metrics(path: Path) -> Dict[str, float]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {k: float(v) for k, v in payload.get("metrics", {}).items()}


def main() -> int:
    args = _parse_args()
    failure_emitter = FailureEmitter(Path("artifacts/failures"))

    if not args.eval_spec.exists():
        failure = FailureLabel(
            Type="reproducibility_failure",
            message="Evaluation spec is missing",
            phase_id="validate",
            evidence={"path": str(args.eval_spec)},
        )
        failure_emitter.emit(failure, run_id=args.run_id)
        print(f"Evaluation checkpoint failed: {failure.as_dict()}")
        return 1

    spec = json.loads(args.eval_spec.read_text(encoding="utf-8"))
    errors = validate_evaluation_spec(
        spec, schema_dir=args.schema_dir, spec_path=args.eval_spec
    )
    if errors:
        failure = FailureLabel(
            Type="schema_failure",
            message="Evaluation spec validation failed",
            phase_id="validate",
            evidence={"errors": errors},
        )
        failure_emitter.emit(failure, run_id=args.run_id)
        print(f"Evaluation checkpoint failed: {failure.as_dict()}")
        return 1
    rollback_artifact = spec.get("rollback_plan", {}).get("artifact")
    if rollback_artifact and not Path(rollback_artifact).exists():
        failure = FailureLabel(
            Type="reproducibility_failure",
            message="Evaluation rollback plan artifact is missing",
            phase_id="validate",
            evidence={"path": rollback_artifact},
        )
        failure_emitter.emit(failure, run_id=args.run_id)
        print(f"Evaluation checkpoint failed: {failure.as_dict()}")
        return 1

    criteria = {
        metric["name"]: metric["threshold"] for metric in spec.get("metrics", [])
    }
    tolerance = float(spec.get("regression_definition", {}).get("tolerance", 0.0))
    checkpointer = EvaluationCheckpointer(
        success_criteria=criteria, tolerance=tolerance
    )

    baseline_metrics = _load_metrics(args.baseline)
    candidate_metrics = _load_metrics(args.candidate)

    checkpointer.record("baseline", baseline_metrics)
    candidate_checkpoint = checkpointer.record("candidate", candidate_metrics)

    deltas = {
        name: candidate_metrics.get(name, 0.0) - baseline_metrics.get(name, 0.0)
        for name in set(baseline_metrics) | set(candidate_metrics)
    }

    override_used = False
    if not candidate_checkpoint.passed and args.allow - breaking - override:
        override_used = True

    report = {
        "anchor": {
            "anchor_id": "evaluation_report",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "scripts.run_evaluation_checkpoint",
            "status": "draft",
        },
        "run_id": args.run_id,
        "eval_id": spec.get("eval_id"),
        "eval_version": spec.get("eval_version"),
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

    args.output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.output_dir / "eval_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    interpret_notes = json.loads(args.candidate.read_text(encoding="utf-8")).get(
        "interpretive_notes", []
    )
    variance_payload = {
        "anchor": {
            "anchor_id": "interpret_variance_notes",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "scripts.run_evaluation_checkpoint",
            "status": "draft",
        },
        "run_id": args.run_id,
        "notes": interpret_notes,
    }
    variance_path = args.output_dir / "interpret_variance_notes.json"
    variance_path.write_text(json.dumps(variance_payload, indent=2), encoding="utf-8")

    if not candidate_checkpoint.passed and not override_used:
        failure = FailureLabel(
            Type="reproducibility_failure",
            message="Evaluation checkpoint failed",
            phase_id="validate",
            evidence={"report": str(report_path)},
        )
        failure_emitter.emit(failure, run_id=args.run_id)
        print(f"Evaluation checkpoint failed: {failure.as_dict()}")
        return 1

    print(f"Evaluation checkpoint passed: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
