import json

import pytest

from generator.recursion_manager import RecursionManager
from modules.llm_adapter import parse_refinement_response, RefinementContract


def test_parse_refinement_response_enforces_contract():
    contract = RefinementContract()
    payload = {
        "decision": "revise",
        "refined_workflow": {"modules": ["a"]},
        "reasoning": "Adds clarity",
        "confidence": 0.72,
        "score_delta": 1.3,
    }

    parsed = parse_refinement_response(json.dumps(payload), contract)
    assert parsed == payload

    payload["decision"] = "unknown"
    with pytest.raises(ValueError):
        parse_refinement_response(json.dumps(payload), contract)


def test_recursion_manager_merges_llm_refinement_payload():
    def fake_generate(prompt: str) -> str:  # pylint: disable=unused-argument
        response = {
            "decision": "accept",
            "refined_workflow": {"summary": "refined", "modules": ["m1"]},
            "reasoning": "Clearer steps",
            "confidence": 0.9,
            "score_delta": 2.1,
        }
        return json.dumps(response)

    workflow = {"workflow_id": "wf-1", "modules": ["m0"]}
    evaluation = {"clarity": 0.5}

    manager = RecursionManager(llm_generate=fake_generate)
    refined = manager.refine_workflow(workflow, evaluation, depth=1)

    assert refined["modules"] == ["m1"]
    metadata = refined.get("recursion_metadata", {})
    assert metadata["llm_decision"] == "accept"
    assert metadata["llm_contract_version"] == manager.contract.version
    assert metadata["llm_status"] == "ok"
