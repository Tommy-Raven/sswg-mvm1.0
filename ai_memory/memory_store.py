#!/usr/bin/env python3
"""
ai_memory/memory_store.py — Persistent workflow storage for SSWG MVM.

Provides a simple filesystem-backed store for workflow snapshots.

Design:
- Each saved workflow becomes a JSON file in `path`.
- Filenames are of the form: {workflow_id}_{YYYYMMDD_%H%M%S}.json
- Optional helpers:
    - list_files(workflow_id?) → list of paths
    - load_latest(workflow_id) → most recent snapshot, if any
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from ai_monitoring.structured_logger import get_logger, log_event


class MemoryStore:
    """
    Filesystem-backed store for workflow JSON snapshots.

    Responsibilities:
    - Save workflow dicts to timestamped JSON files.
    - List stored files, optionally filtered by workflow_id.
    - Load the latest snapshot for a given workflow_id.
    """

    def __init__(self, path: str = "./data/workflows") -> None:
        self.path = path
        os.makedirs(self.path, exist_ok=True)
        self.logger = get_logger("memory")

    # ------------------------------------------------------------------ #
    # Core persistence
    # ------------------------------------------------------------------ #
    def save(self, workflow: Dict[str, Any]) -> str:
        """
        Persist a workflow dict to disk as a timestamped JSON file.

        Args:
            workflow: Workflow dict containing at least "workflow_id".

        Returns:
            The path of the written JSON file.
        """
        workflow_id = str(workflow.get("workflow_id", "unnamed"))
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{workflow_id}_{timestamp}.json"
        file_path = os.path.join(self.path, filename)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file_handle:
            json.dump(workflow, file_handle, indent=2)

        log_event(
            self.logger,
            "memory_save",
            {"workflow_id": workflow_id, "file": file_path},
        )
        return file_path

    # ------------------------------------------------------------------ #
    # Convenience helpers
    # ------------------------------------------------------------------ #
    def list_files(self, workflow_id: Optional[str] = None) -> List[str]:
        """
        List stored workflow JSON files.

        Args:
            workflow_id: If provided, only return files whose name starts
                         with this workflow_id prefix.

        Returns:
            Sorted list of file paths.
        """
        if not os.path.isdir(self.path):
            return []

        files = [
            os.path.join(self.path, filename)
            for filename in os.listdir(self.path)
            if filename.endswith(".json")
        ]

        if workflow_id is not None:
            prefix = f"{workflow_id}_"
            files = [
                path for path in files if os.path.basename(path).startswith(prefix)
            ]

        return sorted(files)

    def load_latest(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Load the most recent snapshot for a given workflow_id, if any.

        Returns:
            Workflow dict or None if no matching file exists / load fails.
        """
        candidates = self.list_files(workflow_id)
        if not candidates:
            return None

        latest_path = candidates[-1]
        try:
            with open(latest_path, "r", encoding="utf-8") as file_handle:
                workflow_data: Dict[str, Any] = json.load(file_handle)
        except (OSError, json.JSONDecodeError):
            log_event(
                self.logger,
                "memory_load_error",
                {"workflow_id": workflow_id, "file": latest_path},
            )
            return None

        log_event(
            self.logger,
            "memory_load_latest",
            {"workflow_id": workflow_id, "file": latest_path},
        )
        return workflow_data
