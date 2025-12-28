"""
Tests workflow regeneration from diff and recursion engine.
"""

from ai_recursive.version_diff_engine import compute_diff_summary
from tests.assertions import require


def test_diff_summary_detects_changes():
    wf_old = {"metadata": {"purpose": "Old"}, "phases": [{"title": "A"}]}
    wf_new = {"metadata": {"purpose": "New"}, "phases": [{"title": "A"}, {"title": "B"}]}

    diff = compute_diff_summary(wf_old, wf_new)
    require(diff["diff_size"] >= 2, "Expected diff size to reflect new phase")
    require(diff["added_phases"] == ["B"], "Expected added phase to be B")
