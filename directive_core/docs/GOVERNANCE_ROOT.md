# === CANONIC LEDGER (TOML) ===
```toml
[anchor]
anchor_id = "sswg_governance_root"
anchor_model = "sswg+mvm"
anchor_version = "1.2.0"
scope = "directive_core/docs"
status = "deprecated"
output_mode = "non_operational_output"

owner = [
  "2025© Raven Recordings",
  "Tommy Raven (Thomas Byers)"
]

init_purpose = "Ratify directive_core as the authoritative governance root. This is explicitly declared non-authoritative. This not the constitution. Validators ignore it for ingestion order."
init_authors = ["Tommy Raven"]
```

## Governance Root Declaration

- `directive_core/` is the single authoritative governance root for this repository.
- Governance resolution MUST source exclusively from `directive_core/docs`.
- Governance-like artifacts outside `directive_core/docs` are non-authoritative and SHALL trigger validation failure.
- `directive_core/docs` inputs take precedence over any other references.
- This is EXPLICITLY declared NON-AUTHORITATIVE.
- This NOT the constitution.
- Validators IGNORE it for ingestion order
