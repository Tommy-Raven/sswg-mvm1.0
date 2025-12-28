"""Versioning helpers for knowledge repository assets.

The meta knowledge repository is responsible for **long-lived creative
memories**. This module defines the canonical revision model for each
domain along with helpers for deriving new revisions from existing ones.

Goals:
- Single source of truth per domain (anchored via ``DomainAnchor``).
- Explicit inheritance between revisions (``parent_revision_id`` is
  required for any non-root revision).
- Predictable conflict resolution rules for cases where two revisions
  disagree.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

TRUST_TIERS = ["observed", "validated", "authoritative"]
TRUST_WEIGHT = {value: index for index, value in enumerate(TRUST_TIERS)}


@dataclass(frozen=True)
class DomainAnchor:
    """Single source of truth for a domain.

    Each domain has exactly one anchor which records the root revision.
    The anchor prevents competing "roots" from emerging and makes it
    clear which revision other artifacts should inherit from.
    """

    domain: str
    root_revision_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"


@dataclass
class DomainRevision:
    """A single revision of a domain definition.

    Attributes:
        domain: Domain identifier (e.g., "story_structure").
        revision_id: Unique identifier for this revision.
        parent_revision_id: The revision this one inherits from. ``None``
            for the root revision only.
        payload: Arbitrary structured content describing the domain.
        trust_tier: Qualitative trust level (``observed`` < ``validated``
            < ``authoritative``).
        rationale: Short note on why this revision was produced.
        sources: Optional upstream references used to build this revision.
        conflicts_resolved: Human-readable descriptions of conflicts
            handled while producing this revision.
        created_at: Timestamp for tie-breaking during conflict resolution.
    """

    domain: str
    revision_id: str
    payload: Dict[str, Any]
    parent_revision_id: Optional[str] = None
    trust_tier: str = "observed"
    rationale: str = ""
    sources: List[str] = field(default_factory=list)
    conflicts_resolved: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def derive(
        self,
        revision_id: str,
        payload_patch: Dict[str, Any],
        rationale: str,
        trust_tier: Optional[str] = None,
        sources: Optional[List[str]] = None,
        conflicts_resolved: Optional[List[str]] = None,
    ) -> "DomainRevision":
        """Create a child revision with explicit inheritance.

        The new revision merges ``payload_patch`` on top of the current
        payload, preserving the inheritance chain via
        ``parent_revision_id``.
        """

        merged_payload = deep_merge(self.payload, payload_patch)
        return DomainRevision(
            domain=self.domain,
            revision_id=revision_id,
            parent_revision_id=self.revision_id,
            payload=merged_payload,
            trust_tier=trust_tier or self.trust_tier,
            rationale=rationale,
            sources=list(sources or self.sources),
            conflicts_resolved=list(conflicts_resolved or []),
        )


def deep_merge(base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge ``patch`` into ``base`` without mutating inputs."""

    merged: Dict[str, Any] = {**base}
    for key, value in patch.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def trust_rank(trust_tier: str) -> int:
    """Return the ordinal rank for a trust tier (lower is weaker)."""

    return TRUST_WEIGHT.get(trust_tier, -1)
