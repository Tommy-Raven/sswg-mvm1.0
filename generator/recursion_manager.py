#!/usr/bin/env python3
"""
generator/recursion_manager.py — Recursion policy and refinement.

Provides:
- RecursionPolicy: configuration for recursion decisions.
- RecursionManager: minimal refinement metadata annotator.
- simple_refiner: MVM-friendly wrapper that makes refinement non-fatal.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from modules.llm_adapter import RefinementContract, generate_refinement

logger = logging.getLogger("generator.recursion_manager")


@dataclass
class RecursionPolicy:
    """
    Configuration for recursion decisions.

    Attributes:
        max_depth:
            Maximum allowed recursion depth.
        min_improvement:
            Minimum score_delta required to justify another recursion step.
    """

    max_depth: int = 2
    min_improvement: float = 1.0


class RecursionManager:
    """
    Decide whether to recurse and generate refined workflow variants.

    At MVM stage, refinement is non-destructive and only annotates metadata.
    """

    def __init__(
        self,
        policy: Optional[RecursionPolicy] = None,
        llm_generate: Optional[Callable[..., str]] = None,
        contract: Optional[RefinementContract] = None,
    ) -> None:
        self.policy = policy or RecursionPolicy()
        self.llm_generate = llm_generate or self._default_llm_generate
        self.contract = contract or RefinementContract()

    @staticmethod
    def _default_llm_generate(prompt: str) -> str:
        """Return a contract-compliant stub when no LLM is wired."""

        logger.info("LLM generation stub invoked with prompt preview: %s", prompt[:200])
        default_response = {
            "decision": "stop",
            "refined_workflow": {},
            "reasoning": "No LLM configured; returning unchanged workflow.",
            "confidence": 0.0,
            "score_delta": 0.0,
        }
        return json.dumps(default_response)

    def should_recurse(self, depth: int, score_delta: float) -> bool:
        """
        Decide if another recursion step is warranted.

        Args:
            depth:
                Current recursion depth (0-based).
            score_delta:
                Improvement score compared to a previous version.

        Returns:
            True if we should recurse further, False otherwise.
        """
        if depth >= self.policy.max_depth:
            return False
        return score_delta >= self.policy.min_improvement

    def refine_workflow(
        self,
        workflow_data: Dict[str, Any],
        evaluation_report: Dict[str, Any],
        depth: int,
    ) -> Dict[str, Any]:
        """
        Generate a refined workflow variant using the LLM contract.

        The LLM is instructed to return a strict JSON payload with the following
        fields (see ``modules.llm_adapter.RefinementContract``):

        - decision: "accept", "revise", or "stop"
        - refined_workflow: dict representing changes or a full replacement
        - reasoning: short natural-language justification
        - confidence: numeric confidence score
        - score_delta: numeric estimate of improvement

        The parsed response is merged into the returned workflow under
        ``recursion_metadata`` for traceability.
        """

        refined_workflow = dict(workflow_data)
        recursion_metadata = refined_workflow.setdefault("recursion_metadata", {})

        try:
            refinement = generate_refinement(
                workflow_data,
                evaluation_report,
                depth,
                llm_generate=self.llm_generate,
                contract=self.contract,
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning("LLM-driven refinement failed; preserving workflow. %s", exc)
            recursion_metadata.update(
                {
                    "depth": depth,
                    "last_evaluation": evaluation_report,
                    "llm_status": "error",
                    "llm_error": str(exc),
                }
            )
            return refined_workflow

        llm_workflow = refinement.get("refined_workflow", {})
        if isinstance(llm_workflow, dict):
            refined_workflow.update(llm_workflow)

        recursion_metadata.update(
            {
                "depth": depth,
                "last_evaluation": evaluation_report,
                "llm_decision": refinement.get("decision"),
                "llm_reasoning": refinement.get("reasoning"),
                "llm_confidence": refinement.get("confidence"),
                "llm_score_delta": refinement.get("score_delta"),
                "llm_contract_version": refinement.get("contract_version"),
                "llm_status": "ok",
            }
        )

        return refined_workflow


def simple_refiner(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal, MVM-friendly refinement wrapper.

    - Uses the local RecursionManager to attach recursion metadata.
    - Supplies safe defaults for evaluation_report and depth.
    - If the RecursionManager API changes or refinement fails, logs a warning
      and returns the original workflow unchanged.

    This ensures the MVM pipeline can rely on refinement being non-fatal.
    """
    # Instantiate the local RecursionManager with default policy.
    manager = RecursionManager()

    # Default evaluation report + depth for MVM stage.
    empty_report: Dict[str, Any] = {}
    depth = 0

    try:
        refined = manager.refine_workflow(workflow, empty_report, depth)
    except TypeError as exc:
        # Signature mismatch or unexpected parameters → soft fail
        logger.warning(
            "Refinement skipped in simple_refiner due to signature mismatch: %s",
            exc,
        )
        return workflow
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # Any other refinement error should not break the MVM pipeline
        logger.warning("Refinement failed in simple_refiner: %s", exc)
        return workflow

    if not isinstance(refined, dict):
        logger.warning(
            "Refinement returned non-dict (%s); returning original workflow.",
            type(refined),
        )
        return workflow

    return refined
