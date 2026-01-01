"""
benchmark_evolution.py
Records temporal benchmark trajectories of epistemic optimization cycles.

Tracks improvement curves for verity, entropy, and throughput
across recursive iterations.
"""

from __future__ import annotations

import statistics
from typing import Any, Dict, List


class BenchmarkEvolution:
    def __init__(self) -> None:
        self.history: Dict[str, List[float]] = {
            "verity": [],
            "entropy": [],
            "determinism": [],
        }

    def log_cycle(self, verity: float, entropy: float, determinism: float) -> None:
        self.history["verity"].append(verity)
        self.history["entropy"].append(entropy)
        self.history["determinism"].append(determinism)

    def convergence_summary(self) -> Dict[str, Any]:
        def trend(metric: str) -> float:
            seq = self.history[metric]
            if len(seq) < 2:
                return 0.0
            return round(seq[-1] - seq[0], 4)

        return {
            "Δverity": trend("verity"),
            "Δentropy": trend("entropy"),
            "Δdeterminism": trend("determinism"),
        }

    def statistical_summary(self) -> Dict[str, Any]:
        def mean(metric: str) -> float:
            seq = self.history[metric]
            return round(statistics.mean(seq), 4) if seq else 0.0

        return {
            "mean_verity": mean("verity"),
            "mean_entropy": mean("entropy"),
            "mean_determinism": mean("determinism"),
        }
