"""Tests for evaluation metric helpers."""

from ai_evaluation.quality_metrics import evaluate_clarity
from tests.assertions import require


def test_evaluate_clarity_scores_valid():
    wf = {
        "phases": [
            {
                "id": "P1",
                "ai_task_logic": "Generate test content for clarity check.",
            }
        ]
    }
    metrics = evaluate_clarity(wf)
    require("clarity_score" in metrics, "Expected clarity_score in metrics output")
    require(metrics["clarity_score"] > 0, "Expected clarity_score to be positive")
