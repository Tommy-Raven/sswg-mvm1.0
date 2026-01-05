> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

---
anchor:
  anchor_id: docs_agent_roles
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# Agent Roles and Cross-Role Communication

This project relies on distinct agent roles to avoid self-confirmation bias and maintain high-quality outputs. Each role has a focused mandate, explicit authority limits, and defined hand-off points to keep generation, critique, and curation independent.

## Roles and Authority Limits

### Creator
- **Purpose:** Drafts new workflows, artifacts, and code based on requirements and schemas.
- **Authority:** May propose and implement changes within scoped tasks; cannot approve its own work for release.
- **Boundaries:** Must leave validation and acceptance decisions to downstream roles.

### Critic
- **Purpose:** Performs adversarial review of Creator outputs for correctness, safety, and alignment with schemas or specifications.
- **Authority:** Can block promotion of artifacts and request revisions; cannot directly alter artifacts except to attach review notes or failing checks.
- **Boundaries:** Must base feedback on evidence (tests, schema results, requirement mapping) and avoid rewriting artifacts independently.

### Curator
- **Purpose:** Consolidates approved artifacts, resolves conflicts, and prepares deliverables for release or publication.
- **Authority:** Can accept or reject artifacts after review, and may request targeted revisions from Creator or Critic.
- **Boundaries:** Should not originate new features or bypass unresolved critiques; decisions must be traceable to review outcomes.

## Cross-Role Communication and Hand-Offs
- **Initial brief → Creator:** Curator supplies requirements, acceptance criteria, and success metrics before creation begins.
- **Creator → Critic hand-off:** Creator provides artifacts plus rationale, change log, and test evidence. No self-approval statements.
- **Critic feedback loop:** Critic records issues with reproducible steps, expected vs. actual behavior, and severity. Feedback travels back to Creator until issues close.
- **Critic → Curator hand-off:** Critic delivers a verdict (approve/block) with citations to tests or checks. Curator only accepts artifacts with an explicit approve verdict.
- **Curator release:** Curator tracks final lineage (what changed, why, and by whom) and documents any remaining risks or follow-up tasks.

## Communication Principles
- Keep communication channels role-scoped: creation discussions with Creator, verification discussions with Critic, release planning with Curator.
- Use shared artifacts (issue trackers, checklists, test reports) instead of informal approvals to prevent circular praise.
- Time-box review cycles and record decisions to avoid stalled hand-offs or ambiguous ownership.
