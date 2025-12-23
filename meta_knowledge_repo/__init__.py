"""Knowledge repository utilities for versioned metadata."""

from meta_knowledge_repo.change_logs import ChangeLog, ChangeLogEntry
from meta_knowledge_repo.evolutions import (
    ConflictResolution,
    MetaKnowledgeRepository,
)
from meta_knowledge_repo.versioning import (
    DomainAnchor,
    DomainRevision,
    TRUST_TIERS,
    deep_merge,
    trust_rank,
)

__all__ = [
    "ChangeLog",
    "ChangeLogEntry",
    "ConflictResolution",
    "DomainAnchor",
    "DomainRevision",
    "MetaKnowledgeRepository",
    "TRUST_TIERS",
    "deep_merge",
    "trust_rank",
]
