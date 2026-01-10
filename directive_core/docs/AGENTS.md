# === CANONIC LEDGER (TOML) ===
```toml
[anchor]
anchor_id = "sswg_agents"
anchor_model = "sswg+mvm+version"
anchor_version = "1.0.0"
scope = "directive_core/docs"
status = "non-authoritative"
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
---

Rules:
The first code fence in the file MUST be TOML
Fence language MUST be toml
No YAML (yaml, yml) fences allowed for anchors
No mixed headers
No duplicated anchors

## Naming Status (Canonical)

Only SSWG/MVM (mindset and ethos) and sswg-mvm (software) are usable. All other variants are deprecated and MUST NOT appear in new or updated content.

See deprecated_nomenclature.md.


---

Root-Scope Agent Rules (Invariant)

These rules apply to all agents, including human contributors, automation, validators, CI systems, and any delegated execution environment.

These rules are non-waivable.


---

Semantic Ambiguity Prohibition (Invariant)

Semantic ambiguity is treated as a security vulnerability, not a stylistic issue.

Agents MUST assume that ambiguous language represents a potential authority bypass, scope escalation, or intent laundering attempt.

Absolute Prohibition

Agents MUST NOT introduce, accept, normalize, interpret, or propagate governance language that relies on conditional permission constructs, including but not limited to:

“allowed unless”

“permitted unless”

“unless explicitly waived”

“allowed with approval”

“may be allowed”

“generally allowed”

“except in special cases”

“at discretion”

“subject to interpretation”


Any appearance of such language SHALL be treated as a violation, regardless of context, intent, or perceived harmlessness.

Absolute Language Requirement

All governance rules, constraints, and prohibitions MUST be expressed using absolute, fail-closed language only:

MUST

MUST NOT

SHALL

SHALL NOT


Language that introduces discretion, interpretation, implied exceptions, or contextual judgment MUST NOT be used to express authority.

Exception Handling (Explicit Only)

If an exception mechanism exists, it MUST be:

1. Defined as a separate, explicitly named contract


2. Governed by its own schema and validator


3. Opt-in by construction, never implied


4. Fully auditable, revocable, and scope-bounded



Exceptions MUST NOT be expressed inline using conditional phrases such as “unless,” “except,” or “with approval.”


---

Mandatory Ambiguity Gate

Agents MUST require the Semantic Ambiguity Gate to pass before any governance ingestion, normalization, or enforcement step.

Ambiguity detection MUST execute prior to schema validation

Ambiguity detection MUST be fail-closed

Ambiguity detection MUST NOT expose rule identifiers, pattern names, or remediation hints in user-visible output



---

Failure Semantics

Any artifact containing semantic ambiguity:

SHALL FAIL CLOSED

SHALL emit the public error label: Semantic Ambiguity

SHALL be quarantined and excluded from further processing

SHALL NOT proceed to normalization, enforcement, or execution

SHALL NOT provide guidance, hints, or corrective suggestions to the submitter


This behavior is mandatory and non-waivable.


---

Interpretation Prohibition

Agents MUST NOT attempt to resolve, reinterpret, or “clarify” ambiguous governance language.

Ambiguity MUST result in rejection, not interpretation.


---

End-of-Document Summary (Normative)

This document establishes that ambiguity is an existential threat to deterministic governance.

By prohibiting conditional permission language, enforcing absolute fail-closed rules, and mandating pre-ingestion ambiguity detection, SSWG/MVM ensures that authority cannot drift, weaken, or be socially engineered.

Any agent, artifact, or system that violates these rules is non-canonical and SHALL be rejected.
