"""Tests for evaluation checkpoints."""

from ai_evaluation.checkpoints import EvaluationCheckpointer


def test_checkpoint_passes_success_criteria():
    manager = EvaluationCheckpointer()
    checkpoint = manager.record(
        "baseline",
        {"overall_score": 0.6, "clarity": 0.7, "coverage": 0.8},
        notes=["Baseline quality is above minimum thresholds."],
    )

    assert checkpoint.passed is True
    assert checkpoint.regressions == {}
    assert manager.summarize()["last_passed"] is True


def test_checkpoint_flags_regression_and_recommends_rollback():
    manager = EvaluationCheckpointer()
    manager.record("baseline", {"overall_score": 0.7, "clarity": 0.7, "coverage": 0.7})

    degraded = manager.record(
        "iteration_2",
        {"overall_score": 0.5, "clarity": 0.4, "coverage": 0.65},
        notes=["Clarity dropped after refinement."],
    )

    assert degraded.passed is False
    assert "clarity" in degraded.regressions
    assert degraded.rollback_recommended is True
    summary = manager.summarize()
    assert summary["rollback_recommended"] is True
