"""
Comprehensive test — ensures end-to-end workflow lifecycle passes
through generation → validation → evaluation → export.
"""

from ai_core.orchestrator import Orchestrator
from ai_core.workflow import Workflow
from ai_validation.schema_validator import validate_workflow
from ai_evaluation.quality_metrics import evaluate_clarity
from ai_visualization.export_manager import export_workflow
import os

from tests.assertions import require

def test_full_workflow_cycle(tmp_path):
    orch = Orchestrator()
    wf = orch.run({"purpose": "E2E test", "audience": "Testers"})
    wf_dict = wf.to_dict()

    valid, err = validate_workflow(wf_dict)
    require(valid, err or "Expected workflow to be valid")

    metrics = evaluate_clarity(wf_dict)
    require(metrics["clarity_score"] > 0, "Expected clarity score to be positive")

    exports = export_workflow(wf_dict, export_mode="json")
    for f in exports.values():
        require(os.path.exists(f), f"Expected export to exist: {f}")


def test_get_default_phases_prefers_id():
    wf = Workflow(
        {
            "phases": [
                {"id": "alpha"},
                {"phase_id": "beta"},
                {"name": "gamma"},
            ]
        }
    )

    require(
        wf.get_default_phases() == ["alpha", "beta", "gamma"],
        "Expected default phase order to prefer ids",
    )
