"""Tests for evaluation metric helpers."""

from ai_evaluation.quality_metrics import evaluate_clarity

def test_evaluate_clarity_scores_valid():
    wf = {
        "phases": [{
            "id": "P1",
            "ai_task_logic": "Generate test content for clarity check."
        }]
    }
    metrics = evaluate_clarity(wf)
    assert "clarity_score" in metrics
    assert metrics["clarity_score"] > 0
