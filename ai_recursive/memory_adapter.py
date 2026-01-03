#!/usr/bin/env python3
"""
ai_recursive/memory_adapter.py — Memory integration for recursive workflows.

This module provides small helpers that connect the recursive subsystem
to the broader memory/history infrastructure.

At MVM, the design goal is to avoid tight coupling:
- We try to use ai_memory.MemoryStore if available.
- We optionally log evolution via generator.history.HistoryManager.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

# Soft imports: provide stubs if modules are not present
try:
    from ai_memory.memory_store import MemoryStore  # type: ignore
except Exception:  # pragma: no cover

    class MemoryStore:  # type: ignore[no-redef]
        def save(self, obj: Dict[str, Any]) -> None:
            pass

        def load_latest(self, key: str) -> Optional[Dict[str, Any]]:
            return None


try:
    from generator.history import HistoryManager  # type: ignore
except Exception:  # pragma: no cover

    class HistoryManager:  # type: ignore[no-redef]
        def record_transition(
            self,
            parent_workflow_id: str,
            child_workflow_id: str,
            score_delta: float,
            modifications=None,
        ):
            return None


class RecursiveMemoryAdapter:
    """
    Facade for storing and retrieving recursive workflow variants.
    """

    def __init__(self) -> None:
        self.memory = MemoryStore()
        self.history = HistoryManager()

    def save_variant(
        self,
        parent_id: str,
        child_workflow: Dict[str, Any],
        modifications,
        score_delta: float = 0.0,
    ) -> None:
        """
        Store a child workflow and record its lineage.
        """
        self.memory.save(child_workflow)
        self.history.record_transition(
            parent_workflow_id=parent_id,
            child_workflow_id=child_workflow.get("workflow_id", "<unnamed>"),
            score_delta=score_delta,
            modifications=list(modifications),
        )

    def load_latest(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the latest workflow snapshot by id, if supported.
        """
        if hasattr(self.memory, "load_latest"):
            return self.memory.load_latest(workflow_id)  # type: ignore[no-any-return]
        return None
