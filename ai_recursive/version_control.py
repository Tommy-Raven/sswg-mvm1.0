#!/usr/bin/env python3
"""
ai_recursive/version_control.py — Version helpers for recursive workflows.

Provides:
- VersionController: manages version strings.
- create_child_version: convenience for creating a child workflow dict,
  updating version, and recording history.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from generator.history import HistoryManager  # soft dependency; module exists in MVM


class VersionController:
    """
    Very simple semantic-version-like controller.

    For MVM, we treat versions as "major.minor.patch" strings and only
    increment the patch component when creating children.
    """

    def next_child_version(self, parent_version: str) -> str:
        parts = (parent_version or "0.0.0").split(".")
        while len(parts) < 3:
            parts.append("0")
        major, minor, patch = parts[:3]
        try:
            patch_int = int(patch)
        except ValueError:
            patch_int = 0
        patch_int += 1
        return f"{major}.{minor}.{patch_int}"


def create_child_version(
    parent_workflow: Dict[str, Any],
    child_body: Dict[str, Any],
    modifications,
    score_delta: float = 0.0,
) -> Dict[str, Any]:
    """
    Create a child workflow dict from a parent + proposed body.

    Steps:
    - Copy `child_body`.
    - Compute a new version string from parent["version"].
    - Preserve `workflow_id` (or allow caller to override beforehand).
    - Record parent/child relation in HistoryManager.

    Returns:
        New child workflow dict.
    """
    vc = VersionController()
    history = HistoryManager()

    parent_id = parent_workflow.get("workflow_id", "<parent-unnamed>")
    parent_version = str(parent_workflow.get("version", "0.0.0"))

    child = deepcopy(child_body)
    child_id = child.get("workflow_id", parent_id)

    new_version = vc.next_child_version(parent_version)
    child["workflow_id"] = child_id
    child["version"] = new_version

    history.record_transition(
        parent_workflow=parent_id,
        child_workflow=child_id,
        modifications=list(modifications),
        score_delta=score_delta,
        metadata={"parent_version": parent_version, "child_version": new_version},
    )

    return child
