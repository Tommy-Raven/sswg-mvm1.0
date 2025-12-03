#!/usr/bin/env python3
"""
ai_recursive/variant_generator.py — Workflow variant generation (MVM stub).

This module defines a small, deterministic way of creating multiple
variants of a given workflow. At MVM stage, it does *not* call LLMs
or external services; it performs structured tweaks to metadata/text
to simulate variant behavior.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


def generate_variants(
    workflow: Dict[str, Any],
    num_variants: int = 3,
) -> List[Dict[str, Any]]:
    """
    Generate a list of variant workflows.

    MVM strategy:
    - For each variant:
        - copy the workflow
        - append a small suffix to the title in metadata
        - optionally tweak a module description (if present)

    This is a placeholder for future, genuinely generative behavior.
    """
    variants: List[Dict[str, Any]] = []
    num_variants = max(0, num_variants)

    for i in range(1, num_variants + 1):
        v = deepcopy(workflow)
        meta = v.setdefault("metadata", {}) or {}

        title = meta.get("title") or v.get("title") or "Workflow"
        meta["title"] = f"{title} (variant {i})"

        # Tweak first module description a bit, if present
        modules = v.get("modules", []) or []
        if modules:
            m0 = modules[0]
            desc = str(m0.get("description") or "")
            suffix = f" [variant {i}]"
            if suffix not in desc:
                m0["description"] = desc + suffix

        variants.append(v)

    return variants
