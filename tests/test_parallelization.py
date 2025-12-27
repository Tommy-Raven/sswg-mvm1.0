"""
Placeholder test for future parallel execution or batch generation features.
Currently checks that the orchestrator can handle multiple runs without conflict.
"""

from ai_core.orchestrator import Orchestrator


def test_parallel_generation_emulation():
    orch = Orchestrator()
    workflows = [orch.run({"purpose": f"Batch {i}"}) for i in range(3)]

    assert len(workflows) == 3
    ids = [wf.to_dict()["workflow_id"] for wf in workflows]
    assert len(set(ids)) == 3, "Workflow IDs should be unique"
