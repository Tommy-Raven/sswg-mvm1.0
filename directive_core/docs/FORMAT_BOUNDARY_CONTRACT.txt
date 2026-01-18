# === CANONIC LEDGER (TOML) ===
```toml
[anchor]
anchor_id = "sswg_format_boundary_contract"
anchor_model = "sswg+mvm+version"
anchor_version = "1.0.0"
scope = "directive_core/docs"
status = "non-authoritative"
output_mode = "non_operational_output"

owner = [
  "2025© Raven Recordings",
  "Tommy Raven (Thomas Byers)"
]

init_purpose = "Mirror of the authoritative FORMAT_BOUNDARY_CONTRACT. Documentation only."
init_authors = ["Tommy Raven"]
```

# ⚠️ NOTICE — NON-AUTHORITATIVE DOCUMENT

This document is non-authoritative and non-operational.

Markdown SHALL NEVER be used for authoritative, operational, or contractual governance.
This file exists solely as a human-readable mirror of the authoritative TOML contract.

# ▶ Authoritative source:
`directive_core/docs/FORMAT_BOUNDARY_CONTRACT.toml`

Validators MUST NOT ingest, interpret, or derive authority from this Markdown file.


---

# Executive Summary

This document mirrors the Format Boundary Contract, which defines the strict, fail-closed rules governing how data formats may cross boundaries between humans, machines, and enforcement layers in the SSWG/MVM system.

The contract exists to:

prevent ambiguity,

eliminate authority bleed,

enforce deterministic ingestion,

and guarantee that machine authority is sourced only from pure TOML.


Any flow not explicitly permitted is forbidden by default.


---

# Canonical Authority Model (Descriptive)

Format	Role	Authority

YAML	Human expression only	❌ No
TOML	Authoritative enforcement surface	✅ Yes
JSON	Canonical machine truth (derived only)	✅ Yes
Markdown	Documentation / presentation only	❌ No


Markdown never carries authority and never flows into machines.


---

# Allowed Flows (Exhaustive)

Only the following flows are permitted:

1. `Human → Machine` (Authoring Path)

human
  → YAML_core
  → Semantic Ambiguity Gate
  → normalize(YAML → TOML)
  → TOML_core (enforced)
  → machine


2. `Machine → Human` (Presentation Path)

machine
  → TOML_core (enforced)
  → render(TOML → Markdown)
  → human


3. `Machine → Machine` (Exchange Path)

machine
  → TOML_core (enforced)
  → machine



These flows are exhaustive.
Any undocumented, implicit, reversed, or round-trip flow is forbidden.


---

# Forbidden Flows (Absolute)

The following flows MUST ALWAYS be rejected:

1. `human → TOML_core`
Humans MUST NOT author authoritative TOML under any circumstance.


2. `machine → YAML_core`
Machines MUST NOT emit YAML as an authority-bearing format.


3. `YAML_core → machine` (without enforcement)
YAML MUST NOT reach machines without ambiguity gating and TOML enforcement.


4. `Markdown → machine`
Markdown is documentation only and NEVER authority-bearing.



There are no waivers, no exceptions, and no discretionary overrides.


---

# Gate Requirements (Descriptive)

`Semantic Ambiguity Gate`

MUST execute before normalization

MUST execute before any validation

MUST be deterministic

MUST fail-closed

MUST emit only the public error label:

`Semantic Ambiguity`



**Internal rule IDs, regexes, or remediation hints MUST NOT be exposed.**


---

# Normalization (YAML → TOML)

MUST be deterministic

MUST expand anchors

MUST eliminate implicit structure

MUST preserve ordering



---

# TOML Enforcement

MUST validate against canonical schemas

MUST forbid additional or unknown properties

MUST treat TOML as the sole enforcement surface



---

# Failure Semantics

On any violation:

Processing fails closed

The artifact is rejected immediately

The artifact is quarantined

The artifact is excluded from ingestion

An audit event MAY be recorded under
`directive_core/artifacts/audit/`


Public errors are generic and non-instructional.
Interpretation, repair, or guidance is forbidden.


---

# Normative Reminder

This Markdown file:

conveys no authority

defines no enforceable rules

exists solely to aid human understanding


All enforcement behavior is defined exclusively in:

▶ `FORMAT_BOUNDARY_CONTRACT.toml`


---

# End-of-Document Summary (Descriptive)

The Format Boundary Contract ensures that:

authority is format-bound,

ambiguity is exterminated,

machines trust only TOML, and

humans never directly author authority.


Any artifact or flow that violates these principles is non-canonical and SHALL be rejected.

This Markdown mirror exists only to document those rules—not to enforce them.
