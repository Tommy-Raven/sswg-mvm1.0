"""Smoke tests for the orchestrator pipeline."""

from ai_core.orchestrator import Orchestrator
from ai_validation.schema_validator import validate_workflow


def test_orchestrator_runs():
    orch = Orchestrator()
    wf = orch.run({"purpose": "Test", "audience": "Dev", "style": "TestStyle"})

    assert wf is not None
    ok, _ = validate_workflow(wf)
    assert ok
