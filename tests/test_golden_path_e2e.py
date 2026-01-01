"""Golden-path end-to-end test for the sswg mvm pipeline."""

from pathlib import Path

from generator.main import DEFAULT_TEMPLATE, run_mvm
from tests.assertions import require


def test_golden_path_end_to_end_run(tmp_path: Path) -> None:
    out_dir = tmp_path / "golden_path"
    refined = run_mvm(
        DEFAULT_TEMPLATE,
        out_dir=out_dir,
        enable_refinement=False,
        enable_history=False,
    )

    require(refined.get("workflow_id"), "Expected workflow_id to be present")
    require(list(out_dir.glob("*.json")), "Expected JSON artifacts to be written")
    require(list(out_dir.glob("*.md")), "Expected Markdown artifacts to be written")
    require(list(out_dir.glob("*.dot")), "Expected Graphviz artifacts to be written")
