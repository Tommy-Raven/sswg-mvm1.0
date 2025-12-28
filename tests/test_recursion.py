"""
Tests recursive generation behavior (meta-learning loop simulation).
"""

from ai_core.orchestrator import Orchestrator

from tests.assertions import require


def test_recursive_generation_behavior():
    orch = Orchestrator()
    wf = orch.run(
        {"purpose": "Recursive test", "audience": "Testers", "mode": "recursive"}
    )
    wf_dict = wf.to_dict()
    require("phases" in wf_dict, "Expected phases in workflow")
    require(isinstance(wf_dict["phases"], list), "Expected phases to be a list")
    require(len(wf_dict["phases"]) > 0, "Expected phases to be non-empty")
