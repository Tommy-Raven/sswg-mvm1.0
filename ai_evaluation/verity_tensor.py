"""
verity_tensor.py
Part of sswg-mvm evaluation subsystem.

Purpose:
Combines semantic clarity, deterministic stability, and entropy efficiency
into a unified verity scalar for epistemic optimization analysis.
"""

from __future__ import annotations

from typing import Any, Dict


def compute_verity_tensor(
    semantic_score: float, det_score: float, entropy: float
) -> float:
    """
    Computes epistemic verity scalar (0-1 range).
    """
    clarity_axis = max(0.0, min(1.0, semantic_score))
    determinism_axis = max(0.0, min(1.0, det_score))
    entropy_axis = max(0.0, min(1.0, 1 - entropy))
    verity_tensor = (clarity_axis * determinism_axis * entropy_axis) ** (1 / 3)
    return round(verity_tensor, 4)


def summarize_tensor_inputs(
    semantic: float, det: float, entropy: float
) -> Dict[str, Any]:
    """
    Diagnostic helper for telemetry export.
    """
    tensor = compute_verity_tensor(semantic, det, entropy)
    return {
        "semantic": semantic,
        "determinism": det,
        "entropy": entropy,
        "verity_tensor": tensor,
    }
