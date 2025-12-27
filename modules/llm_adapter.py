"""Lightweight refinement adapter with deterministic defaults."""
"""LLM adapter for recursion-aware refinement.

from __future__ import annotations

from dataclasses import dataclass, field
import json
from textwrap import dedent
from typing import Any, Callable, Dict


def generate_text(prompt: str) -> str:
    """
    Produce a deterministic, prompt-aware suggestion string.

    This keeps the demo pipeline self-contained while still surfacing the
    prompt context that triggered regeneration.
    """

    cleaned = " ".join(prompt.split())
    return dedent(
        f"""
        Improvement requested based on: {cleaned}\n
        - Clarify ambiguous steps with concrete inputs and outputs.
        - Add explicit owner + success criteria for each phase.
        - Tighten module dependencies and ensure evaluation hooks run.
        """
    ).strip()


@dataclass
class RefinementContract:
    """Contract for parsing LLM-driven refinement payloads."""

    version: str = "1.0"
    allowed_decisions: tuple = ("accept", "revise", "stop")
    required_fields: tuple = (
        "decision",
        "refined_workflow",
        "reasoning",
        "confidence",
        "score_delta",
    )
    field_validators: Dict[str, Callable[[Any], bool]] = field(
        default_factory=lambda: {
            "decision": lambda value: isinstance(value, str),
            "refined_workflow": lambda value: isinstance(value, dict),
            "reasoning": lambda value: isinstance(value, str),
            "confidence": lambda value: isinstance(value, (int, float)),
            "score_delta": lambda value: isinstance(value, (int, float)),
        }
    )

    def validate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        for field_name in self.required_fields:
            if field_name not in payload:
                raise ValueError(f"Missing required field: {field_name}")
            validator = self.field_validators.get(field_name, lambda _: True)
            if not validator(payload[field_name]):
                raise ValueError(f"Invalid type for field: {field_name}")

        decision = payload.get("decision")
        if decision not in self.allowed_decisions:
            raise ValueError(f"Unsupported decision: {decision}")
        return payload


def parse_refinement_response(
    raw_response: str, contract: RefinementContract
) -> Dict[str, Any]:
    """Parse and validate an LLM refinement response."""

    try:
        payload = json.loads(raw_response)
    except json.JSONDecodeError as exc:  # pylint: disable=broad-exception-caught
        raise ValueError("LLM response is not valid JSON") from exc

    return contract.validate(payload)


def _default_llm_generate(prompt: str) -> str:
    """Fallback generator that wraps :func:`generate_text` in a contract payload."""

    suggestion = generate_text(prompt)
    response = {
        "decision": "revise",
        "refined_workflow": {"recursion_hint": suggestion},
        "reasoning": "Offline refinement stub based on deterministic adapter.",
        "confidence": 0.0,
        "score_delta": 0.0,
    }
    return json.dumps(response)


def generate_refinement(
    workflow_data: Dict[str, Any],
    evaluation_report: Dict[str, Any],
    depth: int,
    *,
    llm_generate: Callable[[str], str] | None = None,
    contract: RefinementContract | None = None,
) -> Dict[str, Any]:
    """Generate and parse an LLM-backed workflow refinement."""

    contract = contract or RefinementContract()
    generator = llm_generate or _default_llm_generate

    prompt = dedent(
        f"""
        You are refining a workflow (depth={depth}).
        Workflow snippet: {json.dumps(workflow_data)[:1200]}
        Evaluation snapshot: {evaluation_report}

        Respond with JSON fields: decision (accept|revise|stop), refined_workflow (object),
        reasoning (string), confidence (number), score_delta (number).
        """
    ).strip()

    raw_response = generator(prompt)
    parsed = parse_refinement_response(raw_response, contract)
    parsed["contract_version"] = contract.version
    return parsed


__all__ = [
    "generate_text",
    "RefinementContract",
    "parse_refinement_response",
    "generate_refinement",
]
    raise RuntimeError(
        "No LLM backend configured. Provide llm_generate to generate_refinement "
        "or monkey-patch modules.llm_adapter.generate_text."
    )
"""
modules/llm_adapter.py — lightweight text generator shim.

This module intentionally keeps generation deterministic for offline demos:
- Accepts a prompt string.
- Returns a short improvement suggestion derived from the prompt.

The goal is to provide a stable hook for RecursionManager without requiring
network calls or external credentials.
"""

from __future__ import annotations

from textwrap import dedent


def generate_text(prompt: str) -> str:
    """
    Produce a deterministic, prompt-aware suggestion string.

    The implementation keeps the demo pipeline self contained while still
    surfacing the prompt context that triggered regeneration.
    """

    cleaned = " ".join(prompt.split())
    return dedent(
        f"""
        Improvement requested based on: {cleaned}\n
        - Clarify ambiguous steps with concrete inputs and outputs.
        - Add explicit owner + success criteria for each phase.
        - Tighten module dependencies and ensure evaluation hooks run.
        """
    ).strip()
