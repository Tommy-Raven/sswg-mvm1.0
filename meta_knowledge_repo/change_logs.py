"""Change log utilities for the metadata knowledge repository.

Change logs answer the question: *what changed and why?* They provide a
traceable narrative for revisions so that downstream artifacts can
explain their lineage and reconcile disagreements deterministically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, List, Optional


@dataclass
class ChangeLogEntry:
    """A single recorded change in the repository."""

    domain: str
    revision_id: str
    summary: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    conflicts: List[str] = field(default_factory=list)
    supersedes: Optional[str] = None


class ChangeLog:
    """Append-only change log for meta knowledge revisions."""

    def __init__(self) -> None:
        self._entries: List[ChangeLogEntry] = []

    def record(
        self,
        domain: str,
        revision_id: str,
        summary: str,
        supersedes: Optional[str] = None,
        conflicts: Optional[Iterable[str]] = None,
    ) -> ChangeLogEntry:
        """Add a new entry to the change log."""

        entry = ChangeLogEntry(
            domain=domain,
            revision_id=revision_id,
            summary=summary,
            supersedes=supersedes,
            conflicts=list(conflicts or []),
        )
        self._entries.append(entry)
        return entry

    def history(self, domain: Optional[str] = None) -> List[ChangeLogEntry]:
        """Return the change history, optionally filtered by domain."""

        if domain is None:
            return list(self._entries)
        return [entry for entry in self._entries if entry.domain == domain]
