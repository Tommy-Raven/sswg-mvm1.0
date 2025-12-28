from __future__ import annotations

from generator.budgeting import evaluate_budgets
from tests.assertions import require


def test_evaluate_budgets_passes_within_limits() -> None:
    spec = {
        "phase_budgets": {"ingest": {"max_duration_sec": 10}},
        "artifact_budgets": [
            {"artifact_class": "telemetry", "paths": ["x"], "max_size_mb": 1}
        ],
        "max_total_duration_sec": 20,
    }
    report = evaluate_budgets(
        budget_spec=spec,
        phase_durations={"ingest": 5},
        artifact_sizes=[
            {
                "artifact_class": "telemetry",
                "paths": ["x"],
                "size_bytes": 1024,
                "missing": [],
                "max_size_mb": 1,
            }
        ],
    )
    require(report["status"] == "pass", "Expected budget report to pass")


def test_evaluate_budgets_fails_on_missing_artifacts() -> None:
    spec = {
        "phase_budgets": {"ingest": {"max_duration_sec": 10}},
        "artifact_budgets": [
            {"artifact_class": "telemetry", "paths": ["x"], "max_size_mb": 1}
        ],
        "max_total_duration_sec": 20,
    }
    report = evaluate_budgets(
        budget_spec=spec,
        phase_durations={"ingest": 5},
        artifact_sizes=[
            {
                "artifact_class": "telemetry",
                "paths": ["x"],
                "size_bytes": 0,
                "missing": ["x"],
                "max_size_mb": 1,
            }
        ],
    )
    require(report["status"] == "fail", "Expected budget report to fail")
