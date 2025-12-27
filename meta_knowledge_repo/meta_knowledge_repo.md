# meta_knowledge_repo — long-term creative memory (MVM)

The meta knowledge repository is the **single source of truth** for
long-lived domain definitions (story worlds, tone guides, character
ontologies, etc.). The memory model prioritizes traceability over size so
that we can explain *why* a fact is present and how it evolved.

## Memory model guarantees

- **Single source of truth per domain:** Each domain is anchored once via
  `DomainAnchor` and all future revisions point back to that root.
- **Explicit inheritance:** Every non-root `DomainRevision` records its
  `parent_revision_id`; derived revisions merge a *patch* onto the parent
  payload rather than overwriting it wholesale.
- **Deterministic conflict resolution:** When memories disagree, the
  repository resolves the conflict by trust tier first, then recency, and
  merges payloads to avoid dropping information.

## Core types

- `DomainAnchor` — declares the authoritative root revision id for a
  domain. Prevents dueling roots.
- `DomainRevision` — structured content plus lineage (parent id,
  trust tier, rationale, sources, and conflicts resolved).
- `ChangeLogEntry` — append-only audit trail describing why a revision
  was recorded and what it superseded.

## Repository behaviors

### Anchoring

```python
repo.anchor_domain(
    domain="story_worlds",
    root_revision=DomainRevision(
        domain="story_worlds",
        revision_id="v1",
        payload={"canon": {"cities": ["Anodyne"]}},
        trust_tier="authoritative",
        rationale="Initial world bible",
    ),
    created_by="lore-team",
)
```

- Enforces a single anchor per domain.
- Rejects root revisions that already declare a parent.

### Inheritance and evolution

```python
repo.inherit(
    domain="story_worlds",
    revision_id="v2",
    payload_patch={"canon": {"cities": ["Anodyne", "Verdance"]}},
    rationale="Added new capital city after expedition",
    trust_tier="validated",
)
```

- Uses `deep_merge` to layer the patch on top of the parent payload.
- Captures rationale and optional sources/flags used to generate the
  update.
- Emits a change log entry noting which revision was superseded.

### Conflict resolution rules

Conflicts are raised when an incoming revision targets an outdated
parent. The repository resolves them deterministically:

1. Higher `trust_tier` wins (`authoritative` > `validated` > `observed`).
2. If trust ties, prefer the freshest `created_at`.
3. Merge payloads to prevent data loss while appending a conflict note to
   `conflicts_resolved`.

The resulting revision becomes the new head; the superseded revision is
still retained for lineage queries.
