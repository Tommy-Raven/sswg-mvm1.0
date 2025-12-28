---
anchor:
  anchor_id: changelog
  anchor_version: "1.0.0"
  scope: documentation
  owner: sswg
  status: draft
---

# Changelog

This changelog tracks notable updates to the sswg-mvm repository. For run
instructions and canonical workflow guidance, refer to `docs/RUNBOOK.md`.

## [v0.0.9mvm]

### Added
- Canonical PDL schemas and the 9-phase pipeline contracts under `schemas/` and `pdl/`.
- PDL validation tooling via `generator/pdl_validator.py` and the example PDL in `pdl/example_full_9_phase.yaml`.
- Audit bundle tooling, promotion readiness validation, and phase evidence bundles in `generator/` and `scripts/`.
- Governance, invariants, and execution policy documents (`governance.yaml`, `invariants.yaml`, `root_contract.yaml`).

### Updated
- Documentation coverage across `docs/` for architecture, recursion, metrics, telemetry, and runbooks.
- Determinism and reproducibility enforcement in generator utilities and audit gate scripts.

### Notes
- Pre-release licensing remains in effect. See `LICENSE.md` and `TERMS_OF_USE.md`.
