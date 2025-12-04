"""
Tests recursive generation behavior (meta-learning loop simulation).
"""

from ai_core.orchestrator import Orchestrator


def test_recursive_generation_behavior():
    orch = Orchestrator()
    assert "phases" in wf
    assert isinstance(wf["phases"], list)
    assert len(wf["phases"]) > 0
    wf = orch.run({"purpose": "Recursive test", "audience": "Testers", "mode": "recursive"})
