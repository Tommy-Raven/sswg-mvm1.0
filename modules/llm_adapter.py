<<<<<<< HEAD
<<<<<<< HEAD
"""LLM adapter for recursion-aware refinement.

This module defines the contract for LLM-in-the-loop refinement and exposes
helpers for building prompts and parsing responses.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Mapping, Optional

logger = logging.getLogger("modules.llm_adapter")


@dataclass(frozen=True)
class RefinementContract:
    """Structured contract for LLM-driven refinement outputs.

    The contract is intentionally strict so downstream consumers can rely on
    deterministic keys and formats.

    Fields expected from the model:
    - ``decision``: one of ``{"accept", "revise", "stop"}``
    - ``refined_workflow``: JSON object representing workflow deltas or a fully
      rewritten workflow. Must be an object/dict.
    - ``reasoning``: short natural-language explanation of the decision.
    - ``confidence``: numeric confidence score (0-1 range recommended).
    - ``score_delta``: numeric delta describing expected improvement.
    """

    version: str = "2024-06"
    required_fields: tuple[str, ...] = (
        "decision",
        "refined_workflow",
        "reasoning",
        "confidence",
        "score_delta",
    )
    allowed_decisions: tuple[str, ...] = ("accept", "revise", "stop")
    format: str = "json"

    @property
    def system_prompt(self) -> str:
        """System prompt describing the response contract."""

        return (
            "You are a workflow refinement model. Respond strictly with JSON that "
            "matches the contract fields: decision (accept|revise|stop), "
            "refined_workflow (object), reasoning (string), confidence (number), "
            "and score_delta (number). Do not include any extra keys or prose."
        )

    def describe(self) -> str:
        """Render a short description of the contract."""

        required = ", ".join(self.required_fields)
        decisions = ", ".join(self.allowed_decisions)
        return (
            f"Contract v{self.version} expects JSON with fields [{required}] "
            f"and decision in {{{decisions}}}."
        )


def build_refinement_prompt(
    workflow_data: Mapping[str, Any],
    evaluation_report: Mapping[str, Any],
    depth: int,
    contract: Optional[RefinementContract] = None,
) -> str:
    """Build a compact prompt for the refinement LLM.

    The prompt contains:
    - Current recursion depth
    - Workflow summary
    - Latest evaluation findings
    - Explicit JSON contract reminder
    """

    active_contract = contract or RefinementContract()
    workflow_summary = json.dumps(workflow_data, indent=2)
    evaluation_summary = json.dumps(evaluation_report, indent=2)

    return (
        f"Recursion depth: {depth}.\n"
        f"Workflow to refine (JSON):\n{workflow_summary}\n\n"
        f"Latest evaluation (JSON):\n{evaluation_summary}\n\n"
        f"Respond with JSON matching: {active_contract.describe()}"
    )


def parse_refinement_response(
    raw_response: str, contract: Optional[RefinementContract] = None
) -> Dict[str, Any]:
    """Parse and validate the LLM refinement response.

    Raises ``ValueError`` if parsing fails or required fields are missing.
    """

    active_contract = contract or RefinementContract()

    try:
        payload: Dict[str, Any] = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM response is not valid JSON: {exc}") from exc

    missing: Iterable[str] = [
        field for field in active_contract.required_fields if field not in payload
    ]
    if missing:
        raise ValueError(f"LLM response missing required fields: {sorted(missing)}")

    decision = payload.get("decision")
    if decision not in active_contract.allowed_decisions:
        raise ValueError(
            f"Invalid decision '{decision}'. Expected one of {active_contract.allowed_decisions}."
        )

    refined_workflow = payload.get("refined_workflow")
    if not isinstance(refined_workflow, dict):
        raise ValueError("refined_workflow must be a JSON object/dict")

    return payload


def generate_refinement(
    workflow_data: Mapping[str, Any],
    evaluation_report: Mapping[str, Any],
    depth: int,
    llm_generate: Callable[..., str],
    contract: Optional[RefinementContract] = None,
) -> Dict[str, Any]:
    """Invoke the LLM with the refinement prompt and parse the result."""

    active_contract = contract or RefinementContract()
    prompt = build_refinement_prompt(workflow_data, evaluation_report, depth, contract)

    # Consumers can pass a callable with any signature that accepts a prompt and
    # returns a string. Keyword arguments are not mandated to keep the adapter
    # flexible across providers.
    raw_response = llm_generate(prompt)
    parsed = parse_refinement_response(raw_response, active_contract)
    parsed["contract_version"] = active_contract.version
    return parsed


# NOTE: ``generate_text`` remains the lightweight adapter entry point for
# environments that expose a global LLM generator. It intentionally raises an
# informative error by default to encourage explicit wiring via ``llm_generate``
# when used in RecursionManager.
def generate_text(prompt: str, **_: Any) -> str:  # pragma: no cover - passthrough
    """Default generate_text placeholder.

    Replace this with the actual LLM provider hook (e.g., OpenAI client) or
    supply a custom ``llm_generate`` function to ``generate_refinement``.
    """

    raise RuntimeError(
        "No LLM backend configured. Provide llm_generate to generate_refinement "
        "or monkey-patch modules.llm_adapter.generate_text."
    )
=======
=======
>>>>>>> 87c21bd (Harden demo recursion pipeline)
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
<<<<<<< HEAD
>>>>>>> 87c21bd (Harden demo recursion pipeline)
=======
>>>>>>> 87c21bd (Harden demo recursion pipeline)
