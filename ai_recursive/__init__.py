#!/usr/bin/env python3
"""
ai_recursive package — Recursive refinement utilities for SSWG MVM.

This package handles:
- Generating workflow variants
- Diffing versions
- Merging variants into improved candidates
- Interfacing with memory/history for iterative refinement
"""

from __future__ import annotations

from .variant_generator import generate_variants
from .merge_engine import merge_variants
from .recursion_manager import (
    ProofStep,
    RecursionProof,
    RecursionBudgetError,
    RecursionCheckpointError,
    RecursionLimitError,
    RecursionManager,
    RecursionSnapshot,
    RecursionTerminationError,
)
from .version_control import (
    VersionController,
    create_child_version,
)
from .version_diff_engine import diff_workflows

__all__ = [
    "generate_variants",
    "merge_variants",
    "RecursionManager",
    "RecursionSnapshot",
    "RecursionProof",
    "ProofStep",
    "RecursionLimitError",
    "RecursionBudgetError",
    "RecursionCheckpointError",
    "RecursionTerminationError",
    "VersionController",
    "create_child_version",
    "diff_workflows",
]


def get_version() -> str:
    """
    Simple version identifier for the recursive subsystem.
    """
    return "ai_recursive-mvm-0.1.0"
