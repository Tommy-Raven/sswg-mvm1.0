#!/usr/bin/env python3
"""
ai_evaluation package — Quality & scoring utilities for SSWG MVM.

Public surface (MVM level):

- evaluate_workflow_quality(workflow_dict) → dict of metrics
- SemanticAnalyzer for basic text/semantic checks
- ScoreAdapter for normalizing external model scores
"""

from __future__ import annotations

from .checkpoints import EvaluationCheckpoint, EvaluationCheckpointer
from .evaluation_engine import evaluate_workflow_quality
from .semantic_analysis import SemanticAnalyzer
from .verity_tensor import compute_verity
from .scoring_adapter import ScoreAdapter

__all__ = [
    "evaluate_workflow_quality",
    "SemanticAnalyzer",
    "ScoreAdapter",
    "EvaluationCheckpoint",
    "EvaluationCheckpointer",
    "compute_verity",
]


def get_version() -> str:
    """
    Simple version identifier for the evaluation subsystem.
    """
    return "ai_evaluation-mvm-0.1.0"
