# Canonic Ledger

```toml
[anchor]
anchor_id = "sswg_format_boundary_contract"
anchor_model = "sswg+mvm+version"
anchor_version = "1.0.0"
scope = "directive_core/docs"
owner = ["2025© Raven Recordings", "Tommy Raven (Thomas Byers)"]
status = "invariant"
output_mode = "non_operational_output"
init_purpose = "Define canonical format boundary flows and enforcement requirements."
init_authors = ["Tommy Raven"]
```

# ⚠️ Notice: This document is non-authoritative, and non-operational⚠️
It is forbidden to use markdown formatting for any authoritative or operational and contractual documentation. ALL markdown documents SHALL NEVER be used authoritatively or operatively. TOML formatting is the only acceptable format for authoritative source. You may view the TOML document-pair equivalent, `directive_core/docs/FORMAT_BOUNDARY_CONTRACT.toml`.



---

## Canonical Format Boundary Rules

This contract is the single authoritative specification for format boundaries between humans, machines, and enforcement layers.

Validators MUST fail if this document is absent or malformed.

Ingestion order MUST include this document at position 4, immediately after `SSWG_CONSTITUTION.md` and before `ARCHITECTURE.md`.

## Allowed Flows

Only the following flows are permitted:

1. human → YAML_core → SemanticAmbiguityGate → normalize(YAML→TOML) → TOML_core(enforced) → machine
2. machine → TOML_core(enforced) → render(TOML→Markdown) → human
3. machine → TOML_core(enforced) → machine

## Forbidden Flows

The following flows are forbidden and MUST be rejected:

1. human → TOML_core (humans must author YAML_core, not TOML_core, there is no waiver, explicit or implicit that may bypass this standard)
2. machine → YAML_core (no YAML as a machine output authority format)
3. YAML_core → machine without normalization + enforcement
4. Markdown → machine as authority-bearing input (Markdown is documentation only)

## Gate Requirements

The SemanticAmbiguityGate MUST run before normalization.

Normalization MUST be deterministic.

TOML enforcement MUST validate against schemas.

No rule IDs or pattern names may appear in user-visible failure output.

All failures MUST be fail-closed.

## Failure Semantics

Error label: Semantic Ambiguity.

Ambiguous YAML inputs MUST be quarantined and exiled from the ingestion candidate set.

The public error message MUST be generic and MUST NOT include hints.

Private audit logging is allowed only under `directive_core/artifacts/audit/`.
