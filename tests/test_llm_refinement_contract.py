import json

import pytest

from generator.recursion_manager import RecursionManager
from modules.llm_adapter import parse_refinement_response, RefinementContract
from tests.assertions import require


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
    require(parsed == payload, "Expected parsed response to match payload")

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

    require(refined["modules"] == ["m1"], "Expected refined modules to match")
    metadata = refined.get("recursion_metadata", {})
    require(metadata["llm_decision"] == "accept", "Expected accept decision")
    require(
        metadata["llm_contract_version"] == manager.contract.version,
        "Expected contract version to match",
    )
    require(metadata["llm_status"] == "ok", "Expected ok status")
