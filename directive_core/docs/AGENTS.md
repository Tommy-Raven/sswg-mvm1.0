# === CANONIC LEDGER (TOML) ===
```toml
[anchor]
anchor_id = "sswg_agents"
anchor_model = "sswg+mvm+version"
anchor_version = "1.0.0"
scope = "directive_core/docs"
status = "invariant"
output_mode = "non_operational_output"

owner = [
  "2025© Raven Recordings",
  "Tommy Raven (Thomas Byers)"
]

init_purpose = "Define canonical agent governance for directive_core."
init_authors = ["Tommy Raven"]
```

## Canonical Header Format (Verbatim Pattern)

Every governance document MUST start like this:

# === CANONIC LEDGER (TOML) ===

```toml
[anchor_example]
anchor_id = "example_id"
anchor_model = "sswg+mvm+version"
anchor_version = "1.0.0"
scope = "directive_core/docs"
status = "invariant"
output_mode = "non_operational_output"

owner = [
  "2025© Raven Recordings",
  "Tommy Raven (Thomas Byers)"
]

init_purpose = "Human-readable purpose statement."
init_authors = ["Tommy Raven"]
```

Rules:
The first code fence in the file MUST be TOML
Fence language MUST be toml
No YAML (yaml, yml) fences allowed for anchors
No mixed headers
No duplicated anchors

## Naming Status (Canonical)

Only **SSWG/MVM** (mindset and ethos) and **sswg-mvm** (software) are usable. All other
variants are deprecated. See
[`deprecated_nomenclature.md`](./deprecated_nomenclature.md).

# Root-scope rules:

### "Agents MUST treat ambiguous governance language as a security vulnerability.”

### “Agents MUST NOT attempt to interpret ambiguity.”

### “Agents MUST require Semantic Ambiguity Gate to pass before any governance ingestion step.”
