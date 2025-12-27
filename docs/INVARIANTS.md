---
anchor:
  anchor_id: invariants_docs
  anchor_version: "1.0.0"
  scope: docs
  owner: docs
  status: draft
---

# Invariants

This repository tracks invariant requirements in machine-readable form via
`schemas/invariants_registry.json`. The registry maps each invariant to the
phases it applies to, enforcement locations, and the failure type that must be
emitted on violations. The canonical invariant declarations remain in
`invariants.yaml` and are enforced through promotion readiness gates.

## Registry expectations

- Every invariant declared in `invariants.yaml` must appear in the registry.
- Each registry entry must list at least one enforcement location.
- Registry documentation links must stay current to preserve audit readiness.

## Evidence expectations

Promotion readiness evidence bundles emit per-phase invariant checks with the
required inputs hash, outputs hash, and pass/fail status for audit review.
