> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

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
anchor_id: invariants-doc
anchor_version: "1.0"
scope: documentation
owner: sswg
status: draft
---

# Canonical invariants source

`invariants.yaml` is the canonical source of truth for sswg/mvm invariants.
`root_contract.yaml` must reference `invariants.yaml` and mirror its invariant
entries exactly; parity is enforced by `scripts/validate_root_contracts.py`.
