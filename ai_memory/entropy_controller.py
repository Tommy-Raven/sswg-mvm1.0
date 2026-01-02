"""
entropy_controller.py
Part of the sswg-mvm memory subsystem.

Purpose:
Implements bounded-cognition control through an entropy budget.
Prevents uncontrolled recursion by monitoring cumulative system entropy.
"""

from __future__ import annotations

from typing import Any, Dict


class EntropyController:
    def __init__(self, max_entropy: float = 1.0) -> None:
        """
        Initialize controller with a maximum entropy budget.
        """
        self.max_entropy = max_entropy
        self.current_entropy = 0.0
        self.history: list[float] = []

    def log_entropy(self, value: float) -> bool:
        """
        Add new entropy observation.
        Returns True if within budget, False if budget exceeded.
        """
        self.current_entropy += value
        self.history.append(value)
        return self.current_entropy <= self.max_entropy

    def remaining_budget(self) -> float:
        return max(self.max_entropy - self.current_entropy, 0.0)

    def summary(self) -> Dict[str, Any]:
        mean = sum(self.history) / len(self.history) if self.history else 0.0
        return {
            "total_entropy": round(self.current_entropy, 4),
            "mean_entropy": round(mean, 4),
            "remaining_budget": round(self.remaining_budget(), 4),
        }


def verify_entropy_budget(
    *,
    controller: EntropyController | None = None,
    entropy_values: list[float] | None = None,
    max_entropy: float = 1.0,
) -> Dict[str, Any]:
    """
    Validate entropy totals against the configured budget.
    """
    if controller is None:
        controller = EntropyController(max_entropy=max_entropy)
        for value in entropy_values or []:
            controller.log_entropy(value)

    summary = controller.summary()
    within_budget = summary["total_entropy"] <= max_entropy
    return {
        "total_entropy": summary["total_entropy"],
        "mean_entropy": summary["mean_entropy"],
        "remaining_budget": summary["remaining_budget"],
        "max_entropy": round(max_entropy, 4),
        "within_budget": within_budget,
    }
