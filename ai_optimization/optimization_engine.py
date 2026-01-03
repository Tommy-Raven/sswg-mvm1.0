#!/usr/bin/env python3
"""
optimization_engine.py
Part of the sswg-mvm Optimization Subsystem.

Implements deterministic-adaptive feedback logic for system optimization.
This engine integrates physical constraints, environmental noise, and
heuristic adjustments to guide epistemic recursion toward maximum throughput
and minimal entropy.
"""

from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ai_core.optimization_loader import load_optimization_map


@dataclass(frozen=True)
class OptimizationState:
    """Snapshot of optimization telemetry for recursion decisions."""

    physical_determinism: float
    dynamic_adaptivity: float
    epistemic_recursion: float
    total_optimization: float
    environmental_entropy: float


class OptimizationEngine:
    """
    OptimizationEngine
    -------------------
    Loads the system optimization ontology and simulates cross-domain
    parameter tuning (constants, variables, and recursion logic).
    """

    def __init__(self, optimization_file: Optional[str] = None) -> None:
        self.optimization_file = Path(optimization_file) if optimization_file else None
        self.data = self._load_optimization_map()

        self.optimization_profile = self.data.get("optimization_profile", {})
        self.workflow_profile = self.data.get("workflow_profile", {})

        self.constants = self._parameters().get("constants", [])
        self.variables = self._parameters().get("variables", [])
        self.logic = self._workflow_logic()

    def _load_optimization_map(self) -> Dict[str, Any]:
        try:
            return load_optimization_map(
                self.optimization_file if self.optimization_file else None
            )
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    def _parameters(self) -> Dict[str, Any]:
        parameters = self.optimization_profile.get("parameters", {})
        return parameters if isinstance(parameters, dict) else {}

    def _workflow_logic(self) -> Dict[str, Any]:
        workflow_logic = self.workflow_profile.get("workflow_logic", {})
        return workflow_logic if isinstance(workflow_logic, dict) else {}

    def recursion_depth_limit(self) -> Optional[int]:
        """Return a recursion depth cap from the optimization ontology, if set."""
        raw_limit = self.logic.get("recursion_depth_limit")
        if raw_limit is None:
            return None
        try:
            return int(raw_limit)
        except (TypeError, ValueError):
            return None

    def entropy_budget_alpha(self) -> float:
        """Return the allowed entropy budget alpha, defaulting to 0.25."""
        raw_budget = self.optimization_profile.get("entropy_budget_alpha")
        if raw_budget is None:
            raw_budget = self.optimization_profile.get("entropy_budget")
        if isinstance(raw_budget, (int, float)):
            return float(raw_budget)
        return 0.25

    # ─────────────────────────────────────────────
    #  Core Computations
    # ─────────────────────────────────────────────
    def compute_deterministic_score(self) -> float:
        """
        Determinism metric derived from constants/variables ratio.
        Represents how stable system configuration is.
        """
        hardware_constant = (
            len(self.constants) if isinstance(self.constants, list) else 0
        )
        complexity_factor = sum(
            len(variable.get("examples", []))
            for variable in self.variables
            if isinstance(variable, dict)
        )
        score = hardware_constant / (1 + complexity_factor)
        return round(score, 4)

    def compute_environmental_noise(self) -> float:
        """
        Deterministic entropy proxy derived from variable example counts.
        """
        constants = (
            max(len(self.constants), 1) if isinstance(self.constants, list) else 1
        )
        examples_count = 0
        for variable in self.variables:
            if not isinstance(variable, dict):
                continue
            examples = variable.get("examples", [])
            if isinstance(examples, list):
                examples_count += len(examples)
        noise = examples_count / (constants * 10)
        return round(max(0.0, min(1.0, noise)), 3)

    def compute_total_optimization(
        self,
        *,
        semantic_delta: float,
        deterministic_delta: float,
    ) -> OptimizationState:
        """
        Combine determinism, adaptivity, and recursion metrics into a summary.
        """
        physical_determinism = self.compute_deterministic_score()
        environmental_entropy = self.compute_environmental_noise()
        dynamic_adaptivity = max(0.0, min(1.0, 1.0 - deterministic_delta))
        epistemic_recursion = max(0.0, min(1.0, semantic_delta))
        total_optimization = (
            physical_determinism + dynamic_adaptivity + epistemic_recursion
        ) / 3.0

        return OptimizationState(
            physical_determinism=round(physical_determinism, 4),
            dynamic_adaptivity=round(dynamic_adaptivity, 4),
            epistemic_recursion=round(epistemic_recursion, 4),
            total_optimization=round(total_optimization, 4),
            environmental_entropy=round(environmental_entropy, 4),
        )

    def optimize_heuristics(
        self, workflow: Dict[str, Any], noise: float
    ) -> Dict[str, Any]:
        """
        Adjust workflow parameters based on measured noise.
        Simulates heuristic tuning to restore stability.
        """
        workflow["thread_pool"] = max(1, int(8 * (1 - noise)))
        workflow["cache_policy"] = "LRU" if noise > 0.15 else "LFU"
        workflow["noise_compensation"] = round(1 - noise, 3)
        workflow["optimization_score"] = self.compute_deterministic_score()
        return workflow

    # ─────────────────────────────────────────────
    #  Memory + Metrics Updates
    # ─────────────────────────────────────────────
    def update_metrics(
        self, memory_store: Dict[str, List[float]]
    ) -> tuple[float, float]:
        """
        Updates system memory with new determinism and entropy readings.
        """
        deterministic = self.compute_deterministic_score()
        entropy = self.compute_environmental_noise()
        memory_store.setdefault("determinism", []).append(deterministic)
        memory_store.setdefault("entropy", []).append(entropy)
        return deterministic, entropy

    def get_telemetry_summary(
        self, memory_store: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """
        Summarizes recent optimization telemetry into averaged results.
        """
        determinism_values = memory_store.get("determinism", [])
        entropy_values = memory_store.get("entropy", [])
        if not determinism_values or not entropy_values:
            return {
                "mean_determinism": 0.0,
                "mean_entropy": 0.0,
                "verity_ratio": 0.0,
            }

        det_mean = sum(determinism_values) / len(determinism_values)
        ent_mean = sum(entropy_values) / len(entropy_values)
        verity_ratio = det_mean / (ent_mean + 0.001)
        return {
            "mean_determinism": round(det_mean, 4),
            "mean_entropy": round(ent_mean, 4),
            "verity_ratio": round(verity_ratio, 4),
        }

    # ─────────────────────────────────────────────
    #  Recursion Control Logic
    # ─────────────────────────────────────────────
    def recursive_optimization_loop(
        self, workflow: Dict[str, Any]
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Executes recursive feedback loop based on workflow logic definition.
        """
        depth_limit = int(self.logic.get("recursion_depth_limit", 5))

        memory_store: Dict[str, List[float]] = {"determinism": [], "entropy": []}
        for depth in range(depth_limit):
            det, noise = self.update_metrics(memory_store)
            workflow = self.optimize_heuristics(workflow, noise)
            delta = abs(det - noise)

            if delta <= 0.02:
                workflow["convergence_depth"] = depth
                break

        summary = self.get_telemetry_summary(memory_store)
        workflow["telemetry_summary"] = summary
        workflow["final_iteration"] = depth + 1
        return workflow, summary
