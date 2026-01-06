# Canonic Ledger
```yaml
anchor:
  anchor_id: "sswg_constitution"
  anchor_model: "sswg+mvm"
  anchor_version: "1.2.0"
  scope: "directive_core/docs"
  owner:
    - "2025© Raven Recordings"
    - "Tommy Raven (Thomas Byers)"
  status: "invariant"
  output_mode: "non_operational_output"
  init_purpose: "Define the canonical SSWG constitution for governance."
  init_authors:
    - "Tommy Raven"
```

## Canonical Governance Ingestion Order

Governance documents MUST be ingested in this exact order:

1. `TERMINOLOGY.md`
2. `SSWG_CONSTITUTION.md`
3. `AGENTS.md`
4. `ARCHITECTURE.md`
5. `FORMAL_GUARANTEES.md`
6. `REFERENCES.md`

Missing or malformed ledger documents SHALL cause governance validation failure.
