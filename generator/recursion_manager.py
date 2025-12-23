#!/usr/bin/env python3
"""
generator/recursion_manager.py — Recursion policy and refinement.

This version wires in semantic deltas (SentenceTransformer embeddings),
quality evaluations, and the offline llm_adapter shim to decide whether
regeneration is worth running. It also emits before/after metric plots so the
pipeline can demonstrate recursive improvement.
"""

from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import importlib

from ai_evaluation.evaluation_engine import evaluate_workflow_quality
from ai_evaluation.semantic_analysis import SemanticAnalyzer
from ai_memory.feedback_integrator import FeedbackIntegrator
from ai_recursive.version_diff_engine import compute_diff_summary
from modules.llm_adapter import generate_text
import json
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from modules.llm_adapter import RefinementContract, generate_refinement

logger = logging.getLogger("generator.recursion_manager")


@dataclass
class RecursionPolicy:
    """Configuration for recursion decisions."""

    max_depth: int = 2
    min_improvement: float = 0.05
    min_semantic_delta: float = 0.08


@dataclass
class RecursionOutcome:
    refined_workflow: Dict[str, Any]
    before_report: Dict[str, Any]
    after_report: Dict[str, Any]
    score_delta: float
    semantic_delta: float
    plot_path: Optional[Path]


class SemanticDeltaCalculator:
    """Compute semantic deltas between workflow snapshots."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.analyzer = SemanticAnalyzer()
        self.model = None
        self._util = None

        module_spec = importlib.util.find_spec("sentence_transformers")
        if module_spec is None:
            logger.warning(
                "sentence-transformers is unavailable; using lexical semantic delta."
            )
            return

        sentence_transformers = importlib.import_module("sentence_transformers")
        self.model = sentence_transformers.SentenceTransformer(model_name)
        self._util = sentence_transformers.util
        logger.info("Loaded SentenceTransformer model: %s", model_name)

    def _flatten_workflow(self, workflow: Dict[str, Any]) -> str:
        blocks = self.analyzer.extract_text_blocks(workflow)
        return "\n".join(blocks)

    def encode(self, workflow: Dict[str, Any]):
        text = self._flatten_workflow(workflow)
        if not self.model:
            return text.lower().split()
        return self.model.encode(text, convert_to_tensor=True)

    def delta(self, before_embedding: Any, after_embedding: Any) -> float:
        if self.model is None:
            before_set = set(before_embedding)
            after_set = set(after_embedding)
            if not before_set and not after_set:
                return 0.0
            overlap = len(before_set.intersection(after_set))
            total = max(len(before_set.union(after_set)), 1)
            return 1.0 - (overlap / total)
        similarity = self._util.cos_sim(before_embedding, after_embedding).item()
        return 1.0 - max(min(similarity, 1.0), -1.0)


class RecursionManager:
    """Decide whether to recurse and generate refined workflow variants."""

    def __init__(
        self,
        policy: Optional[RecursionPolicy] = None,
        *,
        output_dir: Path = Path("data/outputs"),
    ) -> None:
        self.policy = policy or RecursionPolicy()
        self.output_dir = output_dir
        self.delta_calculator = SemanticDeltaCalculator()
        self.feedback = FeedbackIntegrator()

    def _evaluate(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        quality = evaluate_workflow_quality(workflow)
        embedding = self.delta_calculator.encode(workflow)
        return {"quality": quality, "embedding": embedding}

    def _render_metric_plot(
        self,
        before_report: Dict[str, Any],
        after_report: Dict[str, Any],
        semantic_delta: float,
    ) -> Path:
        metrics = ["overall_score", "clarity", "coverage", "coherence", "specificity"]
        before_scores = [
            before_report["quality"]["overall_score"],
            *[
                before_report["quality"]["metrics"].get(name, 0.0)
                for name in metrics[1:]
            ],
        ]
        after_scores = [
            after_report["quality"]["overall_score"],
            *[
                after_report["quality"]["metrics"].get(name, 0.0)
                for name in metrics[1:]
            ],
        ]

        width = 720
        height = 360
        padding = 60
        bar_width = 30
        gap = 30
        y_scale = height - 2 * padding

        def _bar_x(idx: int, offset: int) -> int:
            return padding + idx * (2 * bar_width + gap) + offset

        svg_parts = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            f'<text x="{width/2}" y="30" text-anchor="middle" font-size="16" font-family="Inter">',
            f"Recursive refinement — semantic Δ={semantic_delta:.3f}",
            "</text>",
        ]

        for idx, metric in enumerate(metrics):
            x_label = padding + idx * (2 * bar_width + gap) + bar_width
            svg_parts.append(
                f'<text x="{x_label}" y="{height - padding/2}" text-anchor="middle" '
                f'font-size="12" font-family="Inter">{metric.title()}</text>'
            )

            for score, color, offset in (
                (before_scores[idx], "#7C3AED", 0),
                (after_scores[idx], "#10B981", bar_width),
            ):
                bar_height = max(score, 0.0) * y_scale
                x = _bar_x(idx, offset)
                y = height - padding - bar_height
                svg_parts.append(
                    f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" '
                    f'fill="{color}" opacity="0.85" />'
                )
                svg_parts.append(
                    f'<text x="{x + bar_width/2}" y="{y - 6}" text-anchor="middle" '
                    f'font-size="10" font-family="Inter">{score:.2f}</text>'
                )

        svg_parts.extend(
            [
                '<rect x="20" y="20" width="12" height="12" fill="#7C3AED" opacity="0.85" />',
                '<text x="40" y="30" font-size="12" font-family="Inter">before</text>',
                '<rect x="100" y="20" width="12" height="12" fill="#10B981" opacity="0.85" />',
                '<text x="120" y="30" font-size="12" font-family="Inter">after</text>',
                "</svg>",
            ]
        )

        self.output_dir.mkdir(parents=True, exist_ok=True)
        plot_path = self.output_dir / "metrics_before_after.svg"
        plot_path.write_text("\n".join(svg_parts), encoding="utf-8")
        return plot_path

    def _propose_regeneration(
        self, workflow: Dict[str, Any], evaluation: Dict[str, Any], depth: int
    ) -> Dict[str, Any]:
        prompt = (
            "Refine workflow to raise quality scores. "
            f"Current overall={evaluation['quality']['overall_score']:.3f}, depth={depth}. "
            f"Metrics={evaluation['quality']['metrics']}"
        )
        suggestion = generate_text(prompt)

        regenerated = deepcopy(workflow)
        recursion_meta = regenerated.setdefault("recursion", {})
        recursion_meta["llm_prompt"] = prompt
        recursion_meta["llm_suggestion"] = suggestion

        for phase in regenerated.get("phases", []):
            if not isinstance(phase, dict):
                continue
            text = phase.get("ai_task_logic") or ""
            phase["ai_task_logic"] = f"{text}\n\nImprovement: {suggestion}".strip()
            break
        else:
            regenerated.setdefault("phases", []).append(
                {
                    "id": "refined_phase",
                    "title": "Refined Guidance",
                    "ai_task_logic": suggestion,
                }
            )
        return regenerated
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
        if depth >= self.policy.max_depth:
            return False
        return score_delta >= self.policy.min_improvement

    def run_cycle(self, workflow_data: Dict[str, Any], depth: int = 0) -> RecursionOutcome:
        baseline_report = self._evaluate(workflow_data)
        candidate = self._propose_regeneration(workflow_data, baseline_report, depth)
        candidate_report = self._evaluate(candidate)

        score_delta = (
            candidate_report["quality"]["overall_score"]
            - baseline_report["quality"]["overall_score"]
        )
        semantic_delta = self.delta_calculator.delta(
            baseline_report["embedding"], candidate_report["embedding"]
        )

        regenerate = self.should_recurse(depth, score_delta) or (
            semantic_delta >= self.policy.min_semantic_delta
        )
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

        final_workflow = candidate if regenerate else workflow_data
        plot_path = self._render_metric_plot(
            baseline_report, candidate_report, semantic_delta
        )

        diff_summary = compute_diff_summary(workflow_data, final_workflow)
        clarity_score = candidate_report["quality"]["metrics"].get("clarity", 0.0)
        self.feedback.record_cycle(
            diff_summary,
            {"clarity_score": clarity_score, "score_delta": score_delta},
            regenerated=regenerate,
        )

        return RecursionOutcome(
            refined_workflow=final_workflow,
            before_report=baseline_report,
            after_report=candidate_report,
            score_delta=score_delta,
            semantic_delta=semantic_delta,
            plot_path=plot_path,
        )


def simple_refiner(workflow: Dict[str, Any], *, output_dir: Path = Path("data/outputs")) -> Dict[str, Any]:
    """MVM-friendly refinement wrapper that uses RecursionManager."""

    manager = RecursionManager(output_dir=output_dir)
    try:
        outcome = manager.run_cycle(workflow, depth=0)
        workflow.setdefault("evaluation", {}).setdefault("before_after", {})[
            "semantic_delta"
        ] = outcome.semantic_delta
        workflow.setdefault("evaluation", {}).setdefault("plots", {})[
            "before_after"
        ] = str(outcome.plot_path)
        workflow.setdefault("evaluation", {}).setdefault("quality", {}).update(
            outcome.after_report["quality"]
        )
        return outcome.refined_workflow
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.warning("Refinement failed in simple_refiner: %s", exc)
        return workflow
