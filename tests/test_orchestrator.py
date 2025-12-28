"""Smoke tests for the orchestrator pipeline."""

from ai_core.orchestrator import Orchestrator
from ai_validation.schema_validator import validate_workflow
from tests.assertions import require


def test_orchestrator_runs():
    orch = Orchestrator()
    wf = orch.run({"purpose": "Test", "audience": "Dev", "style": "TestStyle"})

    require(wf is not None, "Expected orchestrator to return workflow")
    ok, _ = validate_workflow(wf)
    require(ok, "Expected workflow to validate")
