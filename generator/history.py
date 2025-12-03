#!/usr/bin/env python3
"""
generator/history.py — Workflow Evolution History for SSWG

Tracks parent/child workflow relationships, modifications, and score deltas.

Example logical record:
{
  "timestamp": "...",
  "parent_workflow": "workflow_001",
  "child_workflow": "workflow_001_v2",
  "modifications": ["Added stage", "Improved clarity"],
  "score_delta": +12
}

This module formalizes that idea as a dataclass + append-only history log.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from ai_monitoring.structured_logger import log_event

HISTORY_DIR = Path(__file__).resolve().parent.parent / "data" / "outputs"
HISTORY_FILE = HISTORY_DIR / "history.jsonl"


@dataclass
class HistoryRecord:
    """
    Represents a single evolution step between two workflows.
    """
    timestamp: float
    parent_workflow: str
    child_workflow: str
    modifications: List[str]
    score_delta: float
    metadata: Dict[str, Any]

    @classmethod
    def create(
        cls,
        parent_workflow: str,
        child_workflow: str,
        modifications: Iterable[str],
        score_delta: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "HistoryRecord":
        return cls(
            timestamp=time.time(),
            parent_workflow=parent_workflow,
            child_workflow=child_workflow,
            modifications=list(modifications),
            score_delta=score_delta,
            metadata=metadata or {},
        )


class HistoryManager:
    """
    Handles persistence and retrieval of HistoryRecord objects for SSWG.

    Storage format:
    - JSON Lines file at data/outputs/history.jsonl
    - One JSON object per line, schema compatible with HistoryRecord.asdict()
    """

    def __init__(self, history_file: Path = HISTORY_FILE) -> None:
        self.history_file = history_file
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Write Operations
    # ------------------------------------------------------------------ #
    def record_transition(
        self,
        parent_workflow: str,
        child_workflow: str,
        modifications: Iterable[str],
        score_delta: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> HistoryRecord:
        """
        Create and append a new history record to the log.
        """
        record = HistoryRecord.create(
            parent_workflow=parent_workflow,
            child_workflow=child_workflow,
            modifications=modifications,
            score_delta=score_delta,
            metadata=metadata,
        )

        self._append_record(record)
        return record

    def _append_record(self, record: HistoryRecord) -> None:
        """
        Append a single record to the history file.
        """
        payload = asdict(record)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with self.history_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")

        log_event(
            "history.record.appended",
            {
                "parent": record.parent_workflow,
                "child": record.child_workflow,
                "score_delta": record.score_delta,
            },
        )

    # ------------------------------------------------------------------ #
    # Read / Query Operations
    # ------------------------------------------------------------------ #
    def load_all(self) -> List[HistoryRecord]:
        """
        Load all history records from the log.
        """
        if not self.history_file.exists():
            return []

        records: List[HistoryRecord] = []
        with self.history_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    records.append(
                        HistoryRecord(
                            timestamp=obj.get("timestamp", 0.0),
                            parent_workflow=obj.get("parent_workflow", ""),
                            child_workflow=obj.get("child_workflow", ""),
                            modifications=obj.get("modifications", []),
                            score_delta=obj.get("score_delta", 0.0),
                            metadata=obj.get("metadata", {}),
                        )
                    )
                except Exception:
                    # skip malformed lines but continue
                    continue

        return records

    def get_lineage(self, workflow_id: str) -> List[HistoryRecord]:
        """
        Return all records where the given workflow appears as parent or child.
        """
        return [
            r
            for r in self.load_all()
            if r.parent_workflow == workflow_id or r.child_workflow == workflow_id
        ]

    def latest_child(self, parent_workflow: str) -> Optional[HistoryRecord]:
        """
        Return the most recent child of a given parent workflow, if any.
        """
        candidates = [
            r for r in self.load_all() if r.parent_workflow == parent_workflow
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda r: r.timestamp)


def get_component() -> HistoryManager:
    """
    Factory used by orchestrator / dependency injection frameworks.
    """
    return HistoryManager()
