"""
Test suite for the sswg-mvm Optimization Subsystem.
Ensures that optimization recursion, determinism scoring,
and entropy compensation operate as expected.
"""

from ai_optimization.optimization_adapter import OptimizationAdapter


def test_recursive_optimization_cycle() -> None:
    adapter = OptimizationAdapter()
    workflow = {"task": "deterministic_self_tuning", "quality": 0.7}
    optimized_workflow = adapter.run_adaptive_cycle(workflow)
    summary = optimized_workflow["optimization_summary"]

    assert "mean_determinism" in summary
    assert "mean_entropy" in summary
    assert 0 <= summary["mean_determinism"] <= 1
    assert 0 <= summary["mean_entropy"] <= 1


def test_combined_verity_score() -> None:
    adapter = OptimizationAdapter()
    dummy_summary = {"verity_ratio": 3.25}
    combined = adapter.compute_combined_verity(
        semantic_score=0.82, summary=dummy_summary
    )
    assert combined > 0
