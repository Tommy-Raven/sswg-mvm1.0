"""Tests for evaluation checkpoints."""

from ai_evaluation.checkpoints import EvaluationCheckpointer
from tests.assertions import require


def test_checkpoint_passes_success_criteria():
    manager = EvaluationCheckpointer()
    checkpoint = manager.record(
        "baseline",
        {"overall_score": 0.6, "clarity": 0.7, "coverage": 0.8},
        notes=["Baseline quality is above minimum thresholds."],
    )

    require(checkpoint.passed is True, "Expected checkpoint to pass")
    require(checkpoint.regressions == {}, "Expected no regressions")
    require(
        manager.summarize()["last_passed"] is True,
        "Expected last_passed to be true",
    )


def test_checkpoint_flags_regression_and_recommends_rollback():
    manager = EvaluationCheckpointer()
    manager.record("baseline", {"overall_score": 0.7, "clarity": 0.7, "coverage": 0.7})

    degraded = manager.record(
        "iteration_2",
        {"overall_score": 0.5, "clarity": 0.4, "coverage": 0.65},
        notes=["Clarity dropped after refinement."],
    )

    require(degraded.passed is False, "Expected degraded checkpoint to fail")
    require(
        "clarity" in degraded.regressions, "Expected clarity regression to be recorded"
    )
    require(
        degraded.rollback_recommended is True,
        "Expected rollback recommendation",
    )
    summary = manager.summarize()
    require(
        summary["rollback_recommended"] is True,
        "Expected summary to recommend rollback",
    )
