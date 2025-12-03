#!/usr/bin/env python3
"""
generator/workflow.py — Phase-level helpers for workflow generation.

Handles each phase method:

- run_phase_1_init      – Initialization
- run_phase_1_5_refine  – Objective Refinement
- run_phase_2_howto     – Human-readable How-To
- run_phase_3_modularize– Modularization
- run_phase_4_evaluate  – Evaluation
- run_phase_5_regeneration – Regeneration (planning only at MVM)
"""

from __future__ import annotations

from typing import Any, Dict

from .utils import log


def run_phase_1_init(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 1 — Initialization.

    Normalize basic fields and construct a high-level objective.
    """
    log("Running Phase 1 — Initialization")
    purpose = params.get("purpose", "").strip()
    audience = params.get("audience", "").strip()
    style = params.get("style", "").strip()

    objective = purpose or "General instructional workflow"
    summary = f"{objective} (for {audience})" if audience else objective

    return {
        "phase": "Phase 1 — Initialization",
        "objective": objective,
        "audience": audience,
        "style": style,
        "summary": summary,
    }


def run_phase_1_5_refine(initial: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 1.5 — Objective Refinement.
    """
    log("Running Phase 1.5 — Objective Refinement")
    objective = initial.get("objective", "")
    audience = initial.get("audience", "")

    refined = objective.strip().rstrip(".")
    if audience:
        refined = (
            f"Provide a clear, step-by-step workflow to "
            f"{refined.lower()} for {audience}."
        )

    constraints = {
        "clarity_first": True,
        "max_depth": 5,
    }

    return {
        "phase": "Phase 1.5 — Objective Refinement",
        "refined_objective": refined,
        "constraints": constraints,
    }


def run_phase_2_howto(refined: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 2 — Human-readable How-To.
    """
    log("Running Phase 2 — How-To Generation")
    objective = refined.get("refined_objective") or refined.get("objective", "")
    steps = [
        "Clarify prerequisites and materials.",
        "Outline the high-level stages required.",
        "Break each stage into clear, actionable steps.",
        "Highlight common pitfalls and safety checks.",
        "Provide a brief summary of expected outcomes.",
    ]

    return {
        "phase": "Phase 2 — How-To Generation",
        "objective": objective,
        "steps": steps,
    }


def run_phase_3_modularize(howto: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 3 — Modularization.
    """
    log("Running Phase 3 — Modularization")
    steps = howto.get("steps", [])
    modules = [
        {
            "id": f"module_{index + 1}",
            "name": f"Step {index + 1}",
            "description": step,
        }
        for index, step in enumerate(steps)
    ]

    return {
        "phase": "Phase 3 — Modularization",
        "modules": modules,
    }


def run_phase_4_evaluate(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 4 — Evaluation.

    MVM stub: return a simple status payload tying back to the workflow_id.
    Concrete metrics are handled by ai_evaluation.
    """
    log("Running Phase 4 — Evaluation")
    return {
        "phase": "Phase 4 — Evaluation",
        "status": "pending_external_metrics",
        "notes": "Use ai_evaluation.EvaluationEngine + SemanticScorer for real scoring.",
        "workflow_id": workflow_data.get("workflow_id"),
    }


def run_phase_5_regeneration(
    original: Dict[str, Any],
    evaluation: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Phase 5 — Regeneration.

    For MVM, this function only *plans* regeneration without mutating
    the workflow. Actual regeneration is handled by the recursive
    subsystem (ai_recursive + RecursionManager).
    """
    log("Running Phase 5 — Regeneration (planning)")
    return {
        "phase": "Phase 5 — Regeneration",
        "regeneration_needed": evaluation.get("status") != "accepted",
        "reason": "Evaluation status is not 'accepted'.",
        "plan": [
            "Adjust instructions for clarity where needed.",
            "Simplify redundant or overlapping steps.",
            "Re-run semantic scoring after adjustments.",
        ],
        "original_workflow_id": original.get("workflow_id"),
    }
