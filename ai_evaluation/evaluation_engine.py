#!/usr/bin/env python3
"""
ai_evaluation/evaluation_engine.py — Quality evaluation engine for SSWG MVM.

High-level orchestration over individual metric functions defined in
`quality_metrics.py`.

It exposes a single entrypoint:

    evaluate_workflow_quality(workflow: dict) -> dict

which returns a structured result suitable to be attached under
workflow["evaluation"]["quality"] or similar.
"""

from __future__ import annotations

from typing import Any, Callable, Dict

from . import quality_metrics as qm

MetricFunc = Callable[[Dict[str, Any]], float]


# Registry of metric names -> functions
_METRICS: Dict[str, MetricFunc] = {}


def _register_default_metrics() -> None:
    """
    Register built-in metrics from quality_metrics.py.

    This assumes that `quality_metrics.py` defines some or all of:
        - coverage_metric(workflow) -> float
        - coherence_metric(workflow) -> float
        - specificity_metric(workflow) -> float

    Missing functions are simply skipped.
    """
    global _METRICS
    if _METRICS:
        return  # already initialized

    candidates = {
        "clarity": getattr(qm, "clarity_metric", None),
        "coverage": getattr(qm, "coverage_metric", None),
        "coherence": getattr(qm, "coherence_metric", None),
        "completeness": getattr(qm, "completeness_metric", None),
        "epistemic_optimization": getattr(qm, "epistemic_optimization_metric", None),
        "intent_alignment": getattr(qm, "intent_alignment_metric", None),
        "specificity": getattr(qm, "specificity_metric", None),
        "throughput": getattr(qm, "throughput_metric", None),
        "usability": getattr(qm, "usability_metric", None),
    }

    _METRICS = {name: func for name, func in candidates.items() if callable(func)}


def evaluate_workflow_quality(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a workflow using the default quality metrics.

    Args:
        workflow: A schema-aligned workflow dict.

    Returns:
        Dict with:
            {
              "overall_score": float,
              "metrics": {name: float, ...}
            }
    """
    _register_default_metrics()

    metrics: Dict[str, float] = {}
    for name, func in _METRICS.items():
        try:
            value = float(func(workflow))
        except Exception:
            value = 0.0
        metrics[name] = value

    if metrics:
        overall = sum(metrics.values()) / len(metrics)
    else:
        overall = 0.0

    return {
        "overall_score": overall,
        "metrics": metrics,
    }
