#!/usr/bin/env python3
"""
generator/history.py — Workflow lineage and change history.

Stores parent/child workflow relationships and score deltas in a simple
JSON file, for later analysis or visualization.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import List


@dataclass
class HistoryRecord:
    """
    Represents a single transition between two workflows.
    """

    timestamp: str
    parent_workflow: str
    child_workflow: str
    modifications: List[str]
    score_delta: float


class HistoryManager:
    """
    Manage storage and retrieval of workflow history records.

    Records are persisted as a JSON list of HistoryRecord dictionaries.
    """

    def __init__(self, storage_path: Path | str = Path("./data/history.json")) -> None:
        self.storage_path = Path(storage_path)
        self._records: List[HistoryRecord] = []
        self._load()

    def _load(self) -> None:
        """Load existing history data from disk, if present."""
        if not self.storage_path.exists():
            return

        try:
            text = self.storage_path.read_text(encoding="utf-8")
            raw_records = json.loads(text)
        except (OSError, json.JSONDecodeError):
            self._records = []
            return

        for item in raw_records:
            self._records.append(
                HistoryRecord(
                    timestamp=item.get("timestamp", ""),
                    parent_workflow=item.get("parent_workflow", ""),
                    child_workflow=item.get("child_workflow", ""),
                    modifications=list(item.get("modifications", [])),
                    score_delta=float(item.get("score_delta", 0)),
                )
            )

    def _save(self) -> None:
        """Persist the current records to disk."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        raw = [asdict(record) for record in self._records]
        self.storage_path.write_text(
            json.dumps(raw, indent=2),
            encoding="utf-8",
        )

    def record_transition(
        self,
        parent_workflow_id: str,
        child_workflow_id: str,
        score_delta: float,
        modifications: List[str] | None = None,
    ) -> HistoryRecord:
        """
        Append a new history record and persist it.

        Args:
            parent_workflow_id:
                Identifier of the source workflow.
            child_workflow_id:
                Identifier of the derived workflow.
            score_delta:
                Change in some evaluation score between parent and child.
            modifications:
                Optional list of human-readable modification summaries.

        Returns:
            The created HistoryRecord.
        """
        record = HistoryRecord(
            timestamp=datetime.utcnow().isoformat() + "Z",
            parent_workflow=parent_workflow_id,
            child_workflow=child_workflow_id,
            modifications=modifications or [],
            score_delta=score_delta,
        )
        self._records.append(record)
        self._save()
        return record

    def find_relations(self, workflow_id: str) -> List[HistoryRecord]:
        """
        Find all history records where the given workflow appears as
        either parent or child.
        """
        return [
            record
            for record in self._records
            if workflow_id in (record.parent_workflow, record.child_workflow)
        ]

    def all_records(self) -> List[HistoryRecord]:
        """Return a copy of all stored history records."""
        return list(self._records)
