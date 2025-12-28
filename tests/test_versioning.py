"""
Tests diff-based version comparison and regeneration trigger.
"""

from ai_recursive.version_diff_engine import compute_diff_summary

from tests.assertions import require


def test_version_diff_comparison_basic():
    old = {"metadata": {"purpose": "A"}, "phases": [{"title": "Phase 1"}]}
    new = {
        "metadata": {"purpose": "B"},
        "phases": [{"title": "Phase 1"}, {"title": "Phase 2"}],
    }

    diff_summary = compute_diff_summary(old, new)
    require(diff_summary["diff_size"] > 0, "Expected diff_size to be non-zero")
    require(
        diff_summary["regeneration_recommended"],
        "Expected regeneration recommendation",
    )
