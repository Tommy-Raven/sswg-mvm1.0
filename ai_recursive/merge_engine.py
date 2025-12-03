#!/usr/bin/env python3
"""
ai_recursive/merge_engine.py — Variant merging for SSWG MVM.

Provides utilities to merge multiple workflow variants into a single
“best effort” child workflow. The MVM strategy is deliberately simple.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List


def merge_variants(
    base_workflow: Dict[str, Any],
    variants: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Merge a base workflow with multiple variants.

    MVM strategy:
    - Start from a deep copy of the base.
    - For metadata:
        - add keys present only in variants
        - for conflicting string fields, prefer the *longest* text
    - For modules:
        - index by module_id
        - merge fields with “longest text wins” heuristic

    This is intentionally naive; the main goal is to provide a stable
    interface and a predictable outcome.
    """
    merged = deepcopy(base_workflow)
    variants_list = list(variants)

    if not variants_list:
        return merged

    # Metadata merge (longest string wins for overlapping keys)
    meta = merged.setdefault("metadata", {}) or {}
    for v in variants_list:
        v_meta = v.get("metadata", {}) or {}
        for k, val in v_meta.items():
            if k not in meta:
                meta[k] = val
            else:
                meta[k] = _prefer_longer_text(meta[k], val)

    # Modules merge by module_id
    base_modules = {m.get("module_id"): m for m in merged.get("modules", []) or []}
    for v in variants_list:
        for m in v.get("modules", []) or []:
            mid = m.get("module_id")
            if not mid:
                continue
            if mid not in base_modules:
                base_modules[mid] = deepcopy(m)
            else:
                base_modules[mid] = _merge_module(base_modules[mid], m)

    merged["modules"] = list(base_modules.values())
    return merged


def _prefer_longer_text(a: Any, b: Any) -> Any:
    """
    If both are strings, return the longer; otherwise prefer non-empty,
    otherwise return b.
    """
    if isinstance(a, str) and isinstance(b, str):
        return a if len(a) >= len(b) else b
    if a in (None, "", []):
        return b
    return a


def _merge_module(base: Dict[str, Any], other: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two module dicts with the same module_id using the
    “longer text wins” heuristic for string fields.
    """
    merged = dict(base)
    for k, v in other.items():
        if k not in merged:
            merged[k] = v
        else:
            merged[k] = _prefer_longer_text(merged[k], v)
    return merged
