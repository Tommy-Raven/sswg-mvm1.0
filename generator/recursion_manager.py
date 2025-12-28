#!/usr/bin/env python3
"""Recursion policy, refinement orchestration, and feedback logging."""

from __future__ import annotations

import importlib
import logging
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from ai_evaluation.evaluation_engine import evaluate_workflow_quality
from ai_evaluation.semantic_analysis import SemanticAnalyzer
from ai_memory.feedback_integrator import FeedbackIntegrator
from ai_memory.memory_store import MemoryStore
from ai_monitoring.structured_logger import log_event
from ai_recursive.version_diff_engine import compute_diff_summary
from ai_validation import (
    ErrorClass,
    ErrorSignal,
    Severity,
    apply_incident,
    build_incident,
    classify_exception,
    recovery_decision,
)
from generator.history import HistoryManager
from modules.llm_adapter import RefinementContract, generate_refinement, generate_text

logger = logging.getLogger("generator.recursion_manager")


@dataclass
class RecursionPolicy:
    """Configuration for recursion decisions."""

    max_depth: int = 2
    min_improvement: float = 0.05
    min_semantic_delta: float = 0.08


@dataclass
class RecursionOutcome:
    """Outcome of a recursion cycle."""

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
        """Flatten workflow content into a plain text representation."""
        blocks = self.analyzer.extract_text_blocks(workflow)
        return "\n".join(blocks)

    def encode(self, workflow: Dict[str, Any]):
        """Encode workflow content into an embedding or lexical tokens."""
        text = self._flatten_workflow(workflow)
        if not self.model:
            return text.lower().split()
        return self.model.encode(text, convert_to_tensor=True)

    def delta(self, before_embedding: Any, after_embedding: Any) -> float:
        """Compute semantic delta between embeddings."""
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


class RecursionManager:  # pylint: disable=too-many-instance-attributes
    """Decide whether to recurse and generate refined workflow variants."""

    def __init__(
        self,
        policy: Optional[RecursionPolicy] = None,
        *,
        output_dir: Path = Path("data/outputs"),
        llm_generate: Optional[Callable[[str], str]] = None,
        contract: Optional[RefinementContract] = None,
    ) -> None:
        self.policy = policy or RecursionPolicy()
        self.output_dir = output_dir
        self.delta_calculator = SemanticDeltaCalculator()
        self.feedback = FeedbackIntegrator()
        self.memory_store = MemoryStore()
        self.history = HistoryManager()
        self.llm_generate = llm_generate
        self.contract = contract or RefinementContract()

    def _ensure_schema_tags(self, workflow: Dict[str, Any]) -> str:
        """Ensure schema version metadata is present for downstream consumers."""

        schema_version = str(workflow.get("schema_version") or "1.0.0")
        workflow["schema_version"] = schema_version
        metadata = workflow.setdefault("metadata", {})
        metadata.setdefault("schema_version", schema_version)
        return schema_version

    def _load_lineage_context(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Load the latest stored snapshot and compute deltas for rationale anchoring."""

        workflow_id = str(
            workflow.get("workflow_id")
            or workflow.get("id")
            or workflow.get("metadata", {}).get("workflow_id", "unnamed")
        )

        previous_snapshot = self.memory_store.load_latest(workflow_id)
        diff_summary: Optional[Dict[str, Any]] = None
        prior_reasoning: Optional[str] = None

        if previous_snapshot:
            diff_summary = compute_diff_summary(previous_snapshot, workflow)
            prior_reasoning = previous_snapshot.get("recursion_metadata", {}).get(
                "llm_reasoning"
            )

        log_event(
            "mvm.recursion.lineage_loaded",
            {
                "workflow_id": workflow_id,
                "has_previous": previous_snapshot is not None,
                "previous_diff_size": (
                    diff_summary.get("diff_size") if diff_summary else 0
                ),
            },
        )

        return {
            "workflow_id": workflow_id,
            "previous_snapshot": previous_snapshot,
            "diff_summary": diff_summary,
            "prior_reasoning": prior_reasoning,
        }

    def _evaluate(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a workflow and return quality + embedding."""
        quality = evaluate_workflow_quality(workflow)
        embedding = self.delta_calculator.encode(workflow)
        return {"quality": quality, "embedding": embedding}

    def _render_metric_plot(
        self,
        before_report: Dict[str, Any],
        after_report: Dict[str, Any],
        semantic_delta: float,
    ) -> Path:
        """Render a simple SVG chart for before/after metrics."""
        # pylint: disable=too-many-locals
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
                x_coord = _bar_x(idx, offset)
                y_coord = height - padding - bar_height
                svg_parts.append(
                    f'<rect x="{x_coord}" y="{y_coord}" width="{bar_width}" height="{bar_height}" '
                    f'fill="{color}" opacity="0.85" />'
                )
                svg_parts.append(
                    f'<text x="{x_coord + bar_width/2}" y="{y_coord - 6}" text-anchor="middle" '
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
        """Return a deterministic fallback refinement proposal."""
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

    def should_recurse(self, depth: int, score_delta: float) -> bool:
        """Return True when the recursion policy allows another cycle."""
        if depth >= self.policy.max_depth:
            return False
        return score_delta >= self.policy.min_improvement

    def refine_workflow(
        self,
        workflow_data: Dict[str, Any],
        evaluation_report: Dict[str, Any],
        depth: int,
        lineage_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a refined workflow variant using the LLM contract."""

        refined_workflow = deepcopy(workflow_data)
        recursion_metadata = refined_workflow.setdefault("recursion_metadata", {})
        if lineage_context and lineage_context.get("prior_reasoning"):
            recursion_metadata.setdefault(
                "prior_reasoning", lineage_context.get("prior_reasoning")
            )

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
            signal = classify_exception(exc, source="refinement")
            decision = recovery_decision(signal.error_class, signal.severity)
            incident = build_incident(
                str(refined_workflow.get("workflow_id", "unnamed")), signal
            )
            apply_incident(refined_workflow, incident, decision)
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

    def run_cycle(
        self, workflow_data: Dict[str, Any], depth: int = 0
    ) -> RecursionOutcome:
        """Run a recursion cycle and return the outcome."""
        # pylint: disable=too-many-locals
        schema_version = self._ensure_schema_tags(workflow_data)
        lineage_context = self._load_lineage_context(workflow_data)

        log_event(
            "mvm.recursion.cycle_started",
            {
                "workflow_id": lineage_context["workflow_id"],
                "depth": depth,
                "schema_version": schema_version,
            },
        )

        baseline_report = self._evaluate(workflow_data)
        candidate = self.refine_workflow(
            workflow_data, baseline_report, depth, lineage_context
        )
        candidate_report = self._evaluate(candidate)

        score_delta = (
            candidate_report["quality"]["overall_score"]
            - baseline_report["quality"]["overall_score"]
        )
        semantic_delta = self.delta_calculator.delta(
            baseline_report["embedding"], candidate_report["embedding"]
        )

        llm_decision = candidate.get("recursion_metadata", {}).get("llm_decision")
        regenerate = llm_decision in {"accept", "revise"} and (
            self.should_recurse(depth, score_delta)
            or semantic_delta >= self.policy.min_semantic_delta
        )

        final_workflow = candidate if regenerate else workflow_data
        if score_delta < 0:
            severity = (
                Severity.MAJOR
                if score_delta <= -self.policy.min_improvement
                else Severity.MINOR
            )
            regression_signal = ErrorSignal(
                message="Quality regression detected after refinement.",
                error_class=ErrorClass.BEHAVIORAL,
                severity=severity,
                source="recursion_evaluation",
                context={
                    "score_delta": score_delta,
                    "baseline_score": baseline_report["quality"]["overall_score"],
                    "candidate_score": candidate_report["quality"]["overall_score"],
                },
            )
            decision = recovery_decision(
                regression_signal.error_class, regression_signal.severity
            )
            incident = build_incident(
                str(final_workflow.get("workflow_id", "unnamed")), regression_signal
            )
            apply_incident(final_workflow, incident, decision)
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

        self.history.record_transition(
            parent_workflow_id=lineage_context["workflow_id"],
            child_workflow_id=lineage_context["workflow_id"],
            score_delta=score_delta,
            modifications=diff_summary.get("changed_fields", []),
        )

        self.memory_store.save(final_workflow)

        log_event(
            "mvm.recursion.cycle_completed",
            {
                "workflow_id": lineage_context["workflow_id"],
                "depth": depth,
                "semantic_delta": semantic_delta,
                "score_delta": score_delta,
                "diff_size": diff_summary.get("diff_size", 0),
                "regenerated": regenerate,
            },
        )

        return RecursionOutcome(
            refined_workflow=final_workflow,
            before_report=baseline_report,
            after_report=candidate_report,
            score_delta=score_delta,
            semantic_delta=semantic_delta,
            plot_path=plot_path,
        )


def simple_refiner(
    workflow: Dict[str, Any], *, output_dir: Path = Path("data/outputs")
) -> Dict[str, Any]:
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
