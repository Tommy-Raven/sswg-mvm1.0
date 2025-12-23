"""Evolution tracking for knowledge repository entries.

This module captures the life cycle of domain knowledge:

- Domains are anchored once to avoid competing "roots".
- Revisions form explicit chains via ``parent_revision_id``.
- Conflicts are resolved deterministically to avoid divergent truths.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from meta_knowledge_repo.change_logs import ChangeLog
from meta_knowledge_repo.versioning import (
    DomainAnchor,
    DomainRevision,
    deep_merge,
    trust_rank,
)


@dataclass
class ConflictResolution:
    """Outcome of resolving two competing revisions."""

    chosen: DomainRevision
    superseded: DomainRevision
    rationale: str


class MetaKnowledgeRepository:
    """In-memory registry for long-lived domain knowledge."""

    def __init__(self) -> None:
        self.anchors: Dict[str, DomainAnchor] = {}
        self.revisions: Dict[str, Dict[str, DomainRevision]] = {}
        self.heads: Dict[str, str] = {}
        self.changelog = ChangeLog()

    # ------------------------------------------------------------------ #
    # Anchoring
    # ------------------------------------------------------------------ #
    def anchor_domain(
        self, domain: str, root_revision: DomainRevision, created_by: str = "system"
    ) -> DomainAnchor:
        """Register the single source of truth for a domain."""

        if domain in self.anchors:
            raise ValueError(f"Domain '{domain}' is already anchored")
        if root_revision.parent_revision_id is not None:
            raise ValueError("Root revision must not declare a parent")

        anchor = DomainAnchor(
            domain=domain,
            root_revision_id=root_revision.revision_id,
            created_by=created_by,
        )
        self.anchors[domain] = anchor
        self.revisions[domain] = {root_revision.revision_id: root_revision}
        self.heads[domain] = root_revision.revision_id

        self.changelog.record(
            domain=domain,
            revision_id=root_revision.revision_id,
            summary="Anchored domain root revision.",
        )
        return anchor

    # ------------------------------------------------------------------ #
    # Revision management
    # ------------------------------------------------------------------ #
    def current(self, domain: str) -> Optional[DomainRevision]:
        head_id = self.heads.get(domain)
        if head_id is None:
            return None
        return self.revisions[domain][head_id]

    def get_revision(self, domain: str, revision_id: str) -> DomainRevision:
        try:
            return self.revisions[domain][revision_id]
        except KeyError as exc:  # pragma: no cover - defensive guard
            raise ValueError(f"Unknown revision '{revision_id}' for domain '{domain}'") from exc

    def add_revision(
        self,
        revision: DomainRevision,
        conflicts: Optional[Iterable[str]] = None,
        summary: str = "Added revision",
    ) -> DomainRevision:
        """Add a revision, resolving conflicts if the head has drifted."""

        self._assert_domain_is_anchored(revision.domain)
        domain_revisions = self.revisions[revision.domain]

        if revision.parent_revision_id and revision.parent_revision_id not in domain_revisions:
            raise ValueError(
                f"Parent revision '{revision.parent_revision_id}' missing for domain '{revision.domain}'"
            )

        if revision.revision_id in domain_revisions:
            raise ValueError(
                f"Revision id '{revision.revision_id}' already exists for domain '{revision.domain}'"
            )

        current_revision = self.current(revision.domain)
        supersedes_id = revision.parent_revision_id
        if current_revision and revision.parent_revision_id != current_revision.revision_id:
            resolution = self._resolve_conflict(current_revision, revision)
            revision = resolution.chosen
            supersedes_id = resolution.superseded.revision_id
            conflicts = list(conflicts or []) + [resolution.rationale]
            summary = f"Resolved conflict; superseded {resolution.superseded.revision_id}"

        if revision.revision_id in domain_revisions:
            # Conflict resolution kept the incumbent; record the clash but
            # do not duplicate the stored revision.
            self.heads[revision.domain] = revision.revision_id
            self.changelog.record(
                domain=revision.domain,
                revision_id=revision.revision_id,
                summary=summary,
                supersedes=supersedes_id,
                conflicts=conflicts,
            )
            return revision

        domain_revisions[revision.revision_id] = revision
        self.heads[revision.domain] = revision.revision_id
        self.changelog.record(
            domain=revision.domain,
            revision_id=revision.revision_id,
            summary=summary,
            supersedes=supersedes_id,
            conflicts=conflicts,
        )
        return revision

    def inherit(
        self,
        domain: str,
        revision_id: str,
        payload_patch: Dict[str, object],
        rationale: str,
        trust_tier: Optional[str] = None,
        sources: Optional[List[str]] = None,
        conflicts: Optional[Iterable[str]] = None,
    ) -> DomainRevision:
        """Create and store a revision that explicitly inherits from head."""

        parent = self.current(domain)
        if parent is None:
            raise ValueError(f"Domain '{domain}' is not anchored")

        candidate = parent.derive(
            revision_id=revision_id,
            payload_patch=payload_patch,
            rationale=rationale,
            trust_tier=trust_tier,
            sources=sources,
            conflicts_resolved=list(conflicts or []),
        )
        return self.add_revision(candidate, conflicts=conflicts, summary=rationale)

    # ------------------------------------------------------------------ #
    # Conflict resolution
    # ------------------------------------------------------------------ #
    def _resolve_conflict(
        self, existing: DomainRevision, incoming: DomainRevision
    ) -> ConflictResolution:
        """Resolve disagreement between the current head and an incoming revision."""

        existing_rank = trust_rank(existing.trust_tier)
        incoming_rank = trust_rank(incoming.trust_tier)

        if incoming_rank > existing_rank:
            rationale = self._format_rationale(
                "Incoming revision has higher trust tier", existing, incoming
            )
            chosen = _merge_with_lineage(existing, incoming)
            superseded = existing
        elif incoming_rank < existing_rank:
            rationale = self._format_rationale(
                "Existing head has higher trust tier", existing, incoming
            )
            chosen = existing
            superseded = incoming
        else:
            if incoming.created_at > existing.created_at:
                rationale = self._format_rationale(
                    "Tied trust tier; prefer freshest revision", existing, incoming
                )
                chosen = _merge_with_lineage(existing, incoming)
                superseded = existing
            else:
                rationale = self._format_rationale(
                    "Tied trust tier; retain incumbent", existing, incoming
                )
                chosen = existing
                superseded = incoming

        return ConflictResolution(chosen=chosen, superseded=superseded, rationale=rationale)

    @staticmethod
    def _format_rationale(reason: str, existing: DomainRevision, incoming: DomainRevision) -> str:
        return (
            f"{reason}: existing={existing.revision_id} ({existing.trust_tier}), "
            f"incoming={incoming.revision_id} ({incoming.trust_tier})"
        )

    def _assert_domain_is_anchored(self, domain: str) -> None:
        if domain not in self.anchors:
            raise ValueError(f"Domain '{domain}' has not been anchored yet")


def _merge_with_lineage(existing: DomainRevision, incoming: DomainRevision) -> DomainRevision:
    """Merge payloads while preserving the incoming lineage."""

    merged_payload = deep_merge(existing.payload, incoming.payload)
    return DomainRevision(
        domain=incoming.domain,
        revision_id=incoming.revision_id,
        parent_revision_id=incoming.parent_revision_id,
        payload=merged_payload,
        trust_tier=incoming.trust_tier,
        rationale=incoming.rationale,
        sources=list(incoming.sources),
        conflicts_resolved=list(incoming.conflicts_resolved)
        + [f"Merged with {existing.revision_id}"],
    )
