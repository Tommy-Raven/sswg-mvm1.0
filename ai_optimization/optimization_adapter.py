#!/usr/bin/env python3
"""
optimization_adapter.py
Adapter between OptimizationEngine and mvm evaluation/recursion layers.
Provides callable hooks for throughput-aware semantic scoring.
"""

from __future__ import annotations

from typing import Any, Dict

from ai_optimization.optimization_engine import OptimizationEngine


class OptimizationAdapter:
    def __init__(self) -> None:
        self.engine = OptimizationEngine()

    def run_adaptive_cycle(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the full optimization recursion on a workflow object.
        Returns the optimized state and metrics summary.
        """
        result, summary = self.engine.recursive_optimization_loop(workflow)
        result["optimization_summary"] = summary
        return result

    def compute_combined_verity(
        self, semantic_score: float, summary: Dict[str, Any]
    ) -> float:
        """
        Combines semantic verity (clarity/coherence) with deterministic stability.
        """
        ratio = summary.get("verity_ratio", 0.0)
        combined = semantic_score * ratio
        return round(combined, 3)
