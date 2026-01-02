#!/usr/bin/env python3
"""
ai_memory package — Long-lived state, feedback, and benchmarks for SSWG MVM.
"""

from __future__ import annotations

from .memory_store import MemoryStore
from .feedback_integrator import FeedbackIntegrator
from .anomaly_detector import AnomalyDetector
from .benchmark_tracker import BenchmarkTracker
from .entropy_controller import verify_entropy_budget

__all__ = [
    "MemoryStore",
    "FeedbackIntegrator",
    "AnomalyDetector",
    "BenchmarkTracker",
    "verify_entropy_budget",
]


def get_version() -> str:
    """
    Return a simple version identifier for the ai_memory subsystem.
    """
    return "ai_memory-mvm-0.1.0"
