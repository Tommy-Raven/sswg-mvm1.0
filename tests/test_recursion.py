"""
Tests recursive generation behavior (meta-learning loop simulation).
"""

from ai_core.orchestrator import Orchestrator


def test_recursive_generation_behavior():
    orch = Orchestrator()
    wf = orch.run({"purpose": "Recursive test", "audience": "Testers", "mode": "recursive"})
    wf_dict = wf.to_dict()
    assert "phases" in wf_dict
    assert isinstance(wf_dict["phases"], list)
    assert len(wf_dict["phases"]) > 0
