#!/usr/bin/env python3
"""
ai_evaluation/checkpoints.py — Evaluation checkpoints for iterative workflows.

Checkpoints provide a structured record of quality metrics per iteration
so teams can detect regressions early and decide when to roll back.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


DEFAULT_CRITERIA: Dict[str, float] = {
    "overall_score": 0.55,
    "clarity": 0.5,
    "coverage": 0.5,
}


@dataclass
class EvaluationCheckpoint:
    """Snapshot of evaluation metrics for a single iteration."""

    name: str
    metrics: Dict[str, float]
    criteria: Dict[str, float]
    notes: List[str] = field(default_factory=list)
    passed: bool = False
    regressions: Dict[str, float] = field(default_factory=dict)
    rollback_recommended: bool = False

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "metrics": self.metrics,
            "criteria": self.criteria,
            "notes": self.notes,
            "passed": self.passed,
            "regressions": self.regressions,
            "rollback_recommended": self.rollback_recommended,
        }


class EvaluationCheckpointer:
    """Manage iterative evaluation checkpoints and regression detection."""

    def __init__(
        self,
        success_criteria: Optional[Dict[str, float]] = None,
        *,
        tolerance: float = 0.02,
    ) -> None:
        self.criteria = success_criteria or DEFAULT_CRITERIA
        self.tolerance = max(0.0, tolerance)
        self.history: List[EvaluationCheckpoint] = []

    def _meets_criteria(self, metrics: Dict[str, float]) -> bool:
        return all(metrics.get(name, 0.0) >= threshold for name, threshold in self.criteria.items())

    def _detect_regressions(self, metrics: Dict[str, float]) -> Dict[str, float]:
        if not self.history:
            return {}

        previous = self.history[-1].metrics
        regressions: Dict[str, float] = {}

        for name, prev_value in previous.items():
            current = metrics.get(name, 0.0)
            delta = current - prev_value
            if delta < -self.tolerance:
                regressions[name] = delta

        return regressions

    def record(
        self,
        name: str,
        metrics: Dict[str, float],
        *,
        notes: Optional[List[str]] = None,
    ) -> EvaluationCheckpoint:
        normalized_metrics = {k: float(v) for k, v in metrics.items()}
        passed = self._meets_criteria(normalized_metrics)
        regressions = self._detect_regressions(normalized_metrics)
        rollback = bool(regressions) and not passed

        checkpoint = EvaluationCheckpoint(
            name=name,
            metrics=normalized_metrics,
            criteria=dict(self.criteria),
            notes=list(notes or []),
            passed=passed,
            regressions=regressions,
            rollback_recommended=rollback,
        )
        self.history.append(checkpoint)
        return checkpoint

    def summarize(self) -> Dict[str, object]:
        """Provide a compact summary for attaching to workflow metadata."""
        if not self.history:
            return {"checkpoints": 0, "last_passed": False, "regressions": {}}

        last = self.history[-1]
        return {
            "checkpoints": len(self.history),
            "last_passed": last.passed,
            "last_name": last.name,
            "regressions": last.regressions,
            "rollback_recommended": last.rollback_recommended,
        }
