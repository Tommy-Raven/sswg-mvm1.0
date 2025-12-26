#!/usr/bin/env python3
"""
ai_evaluation/quality_metrics.py — Workflow quality metrics for SSWG MVM.

Contains small, deterministic metric functions that operate on a schema-style
workflow dict.

Existing behavior preserved:
- `evaluate_clarity(wf)` returns {"clarity_score": float}

New MVM-style scalar metrics:
- clarity_metric(workflow)     -> float
- coverage_metric(workflow)    -> float
- coherence_metric(workflow)   -> float
- specificity_metric(workflow) -> float
- completeness_metric(workflow) -> float
- intent_alignment_metric(workflow) -> float
- usability_metric(workflow) -> float
"""

from __future__ import annotations

from typing import Any, Dict, List

_STOP_WORDS = {
    "a",
    "an",
    "and",
    "the",
    "of",
    "to",
    "in",
    "for",
    "with",
    "on",
    "by",
    "as",
    "at",
    "is",
    "are",
    "be",
    "from",
    "or",
    "that",
    "this",
}

from .semantic_analysis import SemanticAnalyzer

_analyzer = SemanticAnalyzer()


# ---------------------------------------------------------------------- #
# Legacy-style clarity evaluator (dict output)
# ---------------------------------------------------------------------- #
def evaluate_clarity(wf: Dict[str, Any]) -> Dict[str, float]:
    """
    Legacy clarity evaluation.

    For each phase, computes a crude clarity score proportional to the
    number of words in `ai_task_logic` (or fallback text), then returns
    the average across phases as "clarity_score".

    Original behavior:
        score_phase = len(text.split()) / 10

    MVM additions:
    - Supports `phase_id` as well as `id`.
    - Avoids division by zero when there are no phases.
    - Clamps per-phase scores to [0, 1] for sanity.
    """
    scores: Dict[str, float] = {}

    for phase in wf.get("phases", []) or []:
        if not isinstance(phase, dict):
            continue

        text = phase.get("ai_task_logic") or phase.get("description") or ""
        phase_id = phase.get("id") or phase.get("phase_id") or "<unnamed>"

        words = len(str(text).split())
        # Original heuristic: len(words) / 10; clamp into [0, 1] band
        raw_score = words / 10.0
        score = max(0.0, min(1.0, raw_score))
        scores[str(phase_id)] = score

    if not scores:
        return {"clarity_score": 0.0}

    avg = sum(scores.values()) / len(scores)
    return {"clarity_score": avg}


# ---------------------------------------------------------------------- #
# Scalar metrics for evaluation_engine
# ---------------------------------------------------------------------- #
def clarity_metric(wf: Dict[str, Any]) -> float:
    """
    Scalar clarity metric: just unwraps evaluate_clarity.
    """
    return float(evaluate_clarity(wf).get("clarity_score", 0.0))


def coverage_metric(wf: Dict[str, Any]) -> float:
    """
    Rough coverage metric: fraction of phases that contain *some* text
    in either `ai_task_logic` or `description`.

    Returns:
        value in [0, 1]
    """
    phases = [p for p in wf.get("phases", []) or [] if isinstance(p, dict)]
    if not phases:
        return 0.0

    covered = 0
    for ph in phases:
        text = ph.get("ai_task_logic") or ph.get("description") or ""
        if str(text).strip():
            covered += 1

    return covered / len(phases)


def coherence_metric(wf: Dict[str, Any]) -> float:
    """
    Very crude coherence proxy based on redundancy of sentences:

    - Extract text blocks using SemanticAnalyzer.
    - Estimate redundancy as unique_sentences / total_sentences.
    - Map redundancy → "coherence" by assuming:
        coherence = redundancy

    Rationale:
    - If everything is copy-pasted, redundancy is low → poor coherence.
    - If sentences are reasonably distinct, redundancy is higher.

    Returns:
        value in [0, 1]
    """
    blocks: List[str] = _analyzer.extract_text_blocks(wf)
    redundancy = _analyzer.estimate_redundancy(blocks)  # in [0, 1]
    # For now, treat redundancy as coherence directly.
    return redundancy


def specificity_metric(wf: Dict[str, Any]) -> float:
    """
    Specificity approximated by average length of text blocks.

    - Compute average characters per block.
    - Map length onto [0, 1] via a simple saturating function:

        score = min(1.0, avg_length / 500)

    So:
        ~0   chars → 0.0
        250  chars → 0.5
        500+ chars → 1.0

    This is a rough heuristic: longer, denser text tends to be more
    specific than ultra-short fragments, but this will be replaced by
    richer analysis later.
    """
    blocks: List[str] = _analyzer.extract_text_blocks(wf)
    avg_len = _analyzer.average_length(blocks)
    return max(0.0, min(1.0, avg_len / 500.0))


def completeness_metric(wf: Dict[str, Any]) -> float:
    """
    Completeness proxy based on presence of phases, tasks, and task contracts.

    Combines:
    - fraction of phases that contain at least one task
    - fraction of tasks that declare both prerequisites and expected outputs
    """
    phases = [p for p in wf.get("phases", []) or [] if isinstance(p, dict)]
    if not phases:
        return 0.0

    phase_with_tasks = 0
    total_tasks = 0
    task_with_contract = 0

    for phase in phases:
        tasks = phase.get("tasks", []) or []
        if tasks:
            phase_with_tasks += 1
        for task in tasks:
            if not isinstance(task, dict):
                continue
            total_tasks += 1
            prerequisites = task.get("prerequisites") or task.get("inputs")
            expected_outputs = task.get("expected_outputs") or task.get("outputs")
            if prerequisites is not None and expected_outputs is not None:
                task_with_contract += 1

    if total_tasks == 0:
        task_score = 0.0
    else:
        task_score = task_with_contract / total_tasks

    phase_score = phase_with_tasks / len(phases)
    return (phase_score + task_score) / 2.0


def intent_alignment_metric(wf: Dict[str, Any]) -> float:
    """
    Intent alignment proxy based on token overlap between workflow intent
    (metadata purpose/description) and phase/task descriptions.
    """
    metadata = wf.get("metadata", {}) or {}
    intent_text = " ".join(
        [
            str(metadata.get("purpose", "")),
            str(metadata.get("description", "")),
            str(metadata.get("title", "")),
        ]
    ).strip()
    if not intent_text:
        return 0.0

    def _tokens(text: str) -> set[str]:
        return {
            token
            for token in "".join(
                [ch.lower() if ch.isalnum() else " " for ch in text]
            ).split()
            if token and token not in _STOP_WORDS
        }

    intent_tokens = _tokens(intent_text)
    if not intent_tokens:
        return 0.0

    blocks: List[str] = _analyzer.extract_text_blocks(wf)
    content_tokens: set[str] = set()
    for block in blocks:
        content_tokens |= _tokens(block)

    if not content_tokens:
        return 0.0

    overlap = intent_tokens.intersection(content_tokens)
    return len(overlap) / len(intent_tokens)


def usability_metric(wf: Dict[str, Any]) -> float:
    """
    Usability proxy based on tasks declaring prerequisites and expected outputs.
    """
    tasks: List[Dict[str, Any]] = []
    for phase in wf.get("phases", []) or []:
        if not isinstance(phase, dict):
            continue
        tasks.extend([t for t in phase.get("tasks", []) or [] if isinstance(t, dict)])

    if not tasks:
        return 0.0

    usable = 0
    for task in tasks:
        prerequisites = task.get("prerequisites") or task.get("inputs")
        expected_outputs = task.get("expected_outputs") or task.get("outputs")
        description = task.get("description") or task.get("action")
        if prerequisites is not None and expected_outputs is not None and description:
            usable += 1

    return usable / len(tasks)
# End of ai_evaluation/quality_metrics.py
