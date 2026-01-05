> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

---
anchor:
  anchor_id: output_guarantees_docs
  anchor_version: "1.0.0"
  scope: docs
  owner: docs
  status: draft
---

# Output guarantees

The promotion readiness pipeline publishes evidence artifacts that guarantee
invariant enforcement across the full 9-phase workflow. For each phase, the
phase evidence bundle records:

- Inputs hash
- Outputs hash
- Invariants checked
- Pass/fail status and failure labels (when present)

Invariant coverage reports must show 100% enforcement of declared invariants
before promotion is allowed.
