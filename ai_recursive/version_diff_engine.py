#!/usr/bin/env python3
"""
ai_recursive/version_diff_engine.py — Diff-based workflow comparison (SSWG MVM)

Compares two workflow versions (as dicts or JSON files) and produces a
structured diff summary. Optionally, a caller-provided regeneration
function can be invoked if the diff exceeds a threshold.

This module is now focused on:
- Computing a structured diff summary.
- Deciding whether regeneration is recommended.
- Recording feedback via ai_memory + ai_evaluation (if available).

It deliberately NO LONGER calls ai_core.Orchestrator directly.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from difflib import unified_diff
from typing import Any, Callable, Dict, Optional

from ai_monitoring.structured_logger import log_event

# Soft imports for feedback + evaluation
try:
    from ai_memory.feedback_integrator import FeedbackIntegrator  # type: ignore
except Exception:  # pragma: no cover

    class FeedbackIntegrator:  # type: ignore[no-redef]
        def record_cycle(self, diff_summary, eval_metrics, regenerated: bool) -> None:
            pass


try:
    from ai_evaluation.quality_metrics import evaluate_clarity  # type: ignore
except Exception:  # pragma: no cover

    def evaluate_clarity(wf: Dict[str, Any]) -> Dict[str, float]:  # type: ignore[no-redef]
        return {"clarity_score": 0.0}


# --------------------------------------------------------------------------- #
# Low-level helpers
# --------------------------------------------------------------------------- #
def load_workflow(path: str) -> Dict[str, Any]:
    """Safely load a JSON workflow file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Workflow not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def diff_strings(str1: str, str2: str) -> str:
    """Return a unified diff string between two text values."""
    diff = unified_diff(
        str1.splitlines(),
        str2.splitlines(),
        fromfile="original",
        tofile="modified",
        lineterm="",
    )
    return "\n".join(diff)


# --------------------------------------------------------------------------- #
# Core diff logic
# --------------------------------------------------------------------------- #
def compute_diff_summary(
    wf_old: Dict[str, Any], wf_new: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compute a structured summary of differences between two workflows.

    Heuristics:
    - metadata changes (key-level)
    - added/removed phases by title
    - modified phases by task list diff

    Returns:
        {
          "changed_fields": [(section, key, old, new), ...],
          "added_phases": [title, ...],
          "removed_phases": [title, ...],
          "modified_phases": [{"title": ..., "diff": ...}, ...],
          "diff_size": int,
          "regeneration_recommended": bool
        }
    """
    summary = {
        "changed_fields": [],
        "added_phases": [],
        "removed_phases": [],
        "modified_phases": [],
        "diff_size": 0,
        "regeneration_recommended": False,
    }

    # Compare metadata
    old_meta = wf_old.get("metadata", {}) or {}
    new_meta = wf_new.get("metadata", {}) or {}
    for key, value in new_meta.items():
        old_value = old_meta.get(key)
        if old_value != value:
            summary["changed_fields"].append(("metadata", key, old_value, value))

    # Compare phase titles
    old_phases = [p for p in wf_old.get("phases", []) or [] if isinstance(p, dict)]
    new_phases = [p for p in wf_new.get("phases", []) or [] if isinstance(p, dict)]

    old_titles = [p.get("title") for p in old_phases if p.get("title")]
    new_titles = [p.get("title") for p in new_phases if p.get("title")]

    for title in new_titles:
        if title not in old_titles:
            summary["added_phases"].append(title)
    for title in old_titles:
        if title not in new_titles:
            summary["removed_phases"].append(title)

    def _format_tasks(tasks: list[Any]) -> str:
        rendered: list[str] = []
        for task in tasks:
            if isinstance(task, dict):
                rendered.append(
                    str(task.get("description") or task.get("id") or task)
                )
            else:
                rendered.append(str(task))
        return "\n".join(rendered)

    # Compare internal logic of shared phases (by title)
    for phase_new in new_phases:
        title_new = phase_new.get("title")
        if not title_new:
            continue
        for phase_old in old_phases:
            if phase_old.get("title") == title_new:
                old_tasks = phase_old.get("tasks", []) or []
                new_tasks = phase_new.get("tasks", []) or []
                old_text = _format_tasks(old_tasks)
                new_text = _format_tasks(new_tasks)
                if old_text != new_text:
                    diff = diff_strings(old_text, new_text)
                    summary["modified_phases"].append(
                        {
                            "title": title_new,
                            "diff": diff,
                        }
                    )

    # Compute diff size heuristic
    summary["diff_size"] = (
        len(summary["changed_fields"])
        + len(summary["added_phases"])
        + len(summary["removed_phases"])
        + len(summary["modified_phases"])
    )

    # Regeneration recommendation (heuristic)
    summary["regeneration_recommended"] = summary["diff_size"] >= 2
    return summary


def diff_workflows(wf_old: Dict[str, Any], wf_new: Dict[str, Any]) -> Dict[str, Any]:
    """
    Public alias for compute_diff_summary, used by ai_recursive.__init__.
    """
    return compute_diff_summary(wf_old, wf_new)


# --------------------------------------------------------------------------- #
# Regeneration decision + feedback
# --------------------------------------------------------------------------- #
def regenerate_if_needed(
    wf_old: Dict[str, Any],
    wf_new: Dict[str, Any],
    threshold: int = 2,
    regen_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Trigger workflow regeneration if the diff exceeds threshold.

    Args:
        wf_old: Original workflow dict.
        wf_new: Modified workflow dict.
        threshold: Minimum diff_size to consider regeneration.
        regen_fn: Optional callable that takes wf_new and returns a
                  regenerated workflow dict. If None, no actual regeneration
                  is performed; only feedback is recorded.

    Behavior:
    - Always compute diff_summary.
    - If diff_size >= threshold and regen_fn is provided:
        - call regen_fn(wf_new) → regenerated
        - evaluate clarity on regenerated
        - record feedback with regenerated=True
    - Else:
        - evaluate clarity on wf_new
        - record feedback with regenerated=False

    Returns:
        Final workflow used (regenerated or wf_new).
    """
    diff_summary = compute_diff_summary(wf_old, wf_new)
    log_event("diff_analysis", diff_summary)

    feedback = FeedbackIntegrator()

    # Decide whether to regenerate
    if diff_summary["diff_size"] >= threshold and regen_fn is not None:
        log_event(
            "regeneration_triggered",
            {"reason": "diff_threshold_exceeded", "threshold": threshold},
        )
        print("🔁 Significant divergence detected. Regeneration requested...")

        regenerated = regen_fn(wf_new)
        eval_metrics = evaluate_clarity(regenerated)
        feedback.record_cycle(diff_summary, eval_metrics, regenerated=True)

        print(
            f"🧠 Feedback integrated. "
            f"New clarity score: {eval_metrics.get('clarity_score', 0.0):.2f}"
        )
        return regenerated

    # No regeneration occurred (either below threshold, or no regen_fn)
    eval_metrics = evaluate_clarity(wf_new)
    feedback.record_cycle(diff_summary, eval_metrics, regenerated=False)

    if diff_summary["diff_size"] >= threshold and regen_fn is None:
        print(
            f"⚠️ Diff above threshold ({diff_summary['diff_size']} ≥ {threshold}) "
            "but no regen function was provided — skipping regeneration."
        )
    else:
        print(
            "✅ Changes below threshold — no regeneration required "
            f"(Clarity {eval_metrics.get('clarity_score', 0.0):.2f})"
        )

    return wf_new


# --------------------------------------------------------------------------- #
# File-based CLI helper
# --------------------------------------------------------------------------- #
def compare_workflows(
    old_path: str,
    new_path: str,
    auto_regen: bool = True,
    regen_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    High-level function for diff-based comparison of two JSON workflow files.

    Args:
        old_path: Path to original workflow JSON.
        new_path: Path to modified workflow JSON.
        auto_regen: If True and regen_fn is provided, call regenerate_if_needed.
        regen_fn: Optional regeneration callable.

    Returns:
        Final workflow dict (regenerated or wf_new).
    """
    wf_old = load_workflow(old_path)
    wf_new = load_workflow(new_path)

    print(f"\nComparing versions:\n- Old: {old_path}\n- New: {new_path}")
    diff_summary = compute_diff_summary(wf_old, wf_new)

    if auto_regen:
        wf_final = regenerate_if_needed(wf_old, wf_new, regen_fn=regen_fn)
    else:
        wf_final = wf_new

    # Persist diff summary for later inspection
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"./data/workflows/workflow_diff_{timestamp}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(diff_summary, f, indent=2)

    print(f"Diff summary saved to: {output_path}")
    return wf_final


# ---------------------- Example Execution ---------------------- #

if __name__ == "__main__":
    # Example paths (replace with actual workflow files)
    old_file = "./data/workflows/workflow_original.json"
    new_file = "./data/workflows/workflow_modified.json"

    if os.path.exists(old_file) and os.path.exists(new_file):
        # No regeneration function in CLI demo; just diff + feedback.
        compare_workflows(old_file, new_file, auto_regen=False)
    else:
        print("ERROR: Example workflow files not found.")
