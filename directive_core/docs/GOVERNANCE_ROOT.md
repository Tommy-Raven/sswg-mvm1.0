# Canonic Ledger
```yaml
anchor:
  anchor_id: "sswg_governance_root"
  anchor_model: "sswg+mvm"
  anchor_version: "1.2.0"
  scope: "directive_core/docs"
  owner:
    - "2025© Raven Recordings"
    - "Tommy Raven (Thomas Byers)"
  status: "invariant"
  output_mode: "non_operational_output"
  init_purpose: "Ratify directive_core as the authoritative governance root."
  init_authors:
    - "Tommy Raven"
```

## Governance Root Declaration

- `directive_core/` is the single authoritative governance root for this repository.
- Governance resolution MUST source exclusively from `directive_core/docs`.
- Governance-like artifacts outside `directive_core/docs` are non-authoritative and SHALL trigger validation failure.
- `directive_core/docs` inputs take precedence over any other references.
