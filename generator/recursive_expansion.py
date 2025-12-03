#!/usr/bin/env python3
"""
generator/recursive_expansion.py — Integration glue for recursive generation.

MVM behavior:
- Does not actually mutate the workflow.
- Attaches a diff summary (computed as old vs. new, currently identity)
  under `recursive_metadata.diff_summary`.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ai_recursive.version_diff_engine import compute_diff_summary


def expand_recursively(
    base_workflow: Dict[str, Any],
    *,
    recursion_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Expand a workflow recursively according to recursion_config.

    For the MVM:
    - Simply shallow-copies the workflow.
    - Computes a diff summary between base_workflow and the copy
      (which will be zero-change, but exercises the diff engine).
    - Attaches diff + recursion_config under `recursive_metadata`.
    """
    expanded: Dict[str, Any] = dict(base_workflow)

    diff_summary = compute_diff_summary(base_workflow, expanded)

    recursive_metadata = expanded.setdefault("recursive_metadata", {})
    recursive_metadata["diff_summary"] = diff_summary
    recursive_metadata["recursion_config"] = recursion_config or {}

    return expanded
