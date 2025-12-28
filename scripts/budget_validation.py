from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from generator.budgeting import (
    collect_artifact_sizes,
    evaluate_budgets,
    load_budget_spec,
)
from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate performance budgets.")
    parser.add_argument(
        "--budget-spec",
        type=Path,
        default=Path("governance/budget_spec.json"),
        help="Budget specification path.",
    )
    parser.add_argument(
        "--telemetry-path",
        type=Path,
        default=Path("artifacts/telemetry/run_telemetry.json"),
        help="Run telemetry path.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path("artifacts/budgets/budget_report.json"),
        help="Output path for budget report.",
    )
    parser.add_argument(
        "--schema-dir",
        type=Path,
        default=Path("schemas"),
        help="Schema directory.",
    )
    parser.add_argument(
        "--run-id", type=str, default="budget-validate", help="Run identifier."
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/budgets/failures"))

    if not args.budget_spec.exists():
        emitter.emit(
            FailureLabel(
                Type="reproducibility_failure",
                message="Budget specification missing",
                phase_id="validate",
                evidence={"path": str(args.budget_spec)},
            ),
            run_id=args.run_id,
        )
        print("Budget validation failed")
        return 1

    spec = load_budget_spec(args.budget_spec)
    schema = json.loads(
        (args.schema_dir / "budget-spec.json").read_text(encoding="utf-8")
    )
    errors = sorted(
        Draft202012Validator(schema).iter_errors(spec), key=lambda e: e.path
    )
    if errors:
        emitter.emit(
            FailureLabel(
                Type="schema_failure",
                message="Budget spec schema validation failed",
                phase_id="validate",
                evidence={
                    "errors": [
                        {"message": error.message, "path": list(error.path)}
                        for error in errors
                    ]
                },
            ),
            run_id=args.run_id,
        )
        print("Budget validation failed")
        return 1

    if not args.telemetry_path.exists():
        emitter.emit(
            FailureLabel(
                Type="reproducibility_failure",
                message="Telemetry artifact missing for budget validation",
                phase_id="validate",
                evidence={"path": str(args.telemetry_path)},
            ),
            run_id=args.run_id,
        )
        print("Budget validation failed")
        return 1

    telemetry = json.loads(args.telemetry_path.read_text(encoding="utf-8"))
    phase_durations = telemetry.get("phase_durations", {})
    artifact_sizes = collect_artifact_sizes(spec.get("artifact_budgets", []))
    report = evaluate_budgets(
        budget_spec=spec,
        phase_durations=phase_durations,
        artifact_sizes=artifact_sizes,
    )
    report["anchor"] = {
        "anchor_id": "budget_report",
        "anchor_version": "1.0.0",
        "scope": "run",
        "owner": "scripts.budget_validation",
        "status": "draft",
    }
    report["run_id"] = telemetry.get("run_id")
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if report.get("status") != "pass":
        emitter.emit(
            FailureLabel(
                Type="reproducibility_failure",
                message="Budget validation failed",
                phase_id="validate",
                evidence={"violations": report.get("violations", [])},
            ),
            run_id=args.run_id,
        )
        print("Budget validation failed")
        return 1

    print("Budget validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
