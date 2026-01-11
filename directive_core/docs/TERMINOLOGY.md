# === CANONIC LEDGER (TOML) ===

```toml
[anchor]
anchor_id = "terminology"
anchor_model = "sswg+mvm+version"
anchor_version = "1.0.0"
scope = "directive_core/docs"
status = "invariant"
output_mode = "non_operational_output"

owner = [
  "2025© Raven Recordings",
  "Tommy Raven (Thomas Byers)"
]

init_purpose = "Define the canonical terminology for SSWG/MVM governance and enforcement."
init_authors = ["Tommy Raven"]
```

# ⚠️ Notice: This document is non-authoritative, and non-operational⚠️
It is forbidden to use markdown formatting for any authoritative or operational and contractual documentation. ALL markdown documents SHALL NEVER be used authoritatively or operatively. TOML formatting is the only acceptable format for authoritative source. You may view the TOML document-pair equivalent, `directive_core/docs/TERMINOLOGY.toml`.



---

## Executive Summary

This document defines the **authoritative and exhaustive terminology** for the SSWG/MVM governance system. It establishes the precise meanings of all governance-relevant terms and explicitly forbids ambiguous, inferred, or colloquial usage.

Terminology is the **first ingestion layer** of governance. All subsequent documents, validators, schemas, and enforcement logic derive semantic meaning from this file. Any artifact that contradicts, weakens, or bypasses these definitions **SHALL** be rejected.

Effective at `anchor_version: 1.0.0`, this terminology set is enforced as a **security boundary**. Ambiguity is treated as a vulnerability, not a documentation defect. The system is intentionally hostile to unclear language.

--- 

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

## 1. Authority and Scope

1. This document **SHALL ALWAYS** be the highest semantic authority within the SSWG/MVM governance system.
2. All governance documents, schemas, validators, logs, and audit artifacts **MUST** use these terms exactly as defined.
3. If a term is not defined here, it **SHALL NOT** be used in any canonical governance context.
4. Terminology violations **MUST** cause fail-closed governance rejection.

---

## 2. Core Governance Principles (Semantic)

* The system enforces constraints; it does not infer intent.
* Authority, scope, and precedence **MUST** be explicit and verifiable.
* Outputs are non-operational artifacts, not instructions.
* Determinism is phase-scoped and explicitly declared.
* Ambiguity is a security risk and **SHALL** be eradicated immediately.

---

## 3. Naming Discipline

| Entity Type        | Format                | Example                                 |
| ------------------ | --------------------- | --------------------------------------- |
| Software           | lowercase, hyphenated | `sswg-mvm`                              |
| Governance mindset | uppercase             | `SSWG`, `MVM`                           |
| Concepts / terms   | snake_case            | `semantic_ambiguity`, `evaluation_gate` |
| Constants          | UPPERCASE             | `FAIL_CLOSED`                           |
| Anchors            | TOML block            | `anchor_id`, `anchor_version`           |

Any deviation **SHALL** be treated as a terminology violation.

---

## 4. Core Term Definitions (Normative)

### 4.1 invariant

A property that **MUST ALWAYS** remain true. Invariants are immutable and non-negotiable.

### 4.2 constraint

A rule that may evolve over time but **MUST NOT** violate invariants.

### 4.3 artifact

A non-operational, inspectable output produced for audit or validation.

### 4.4 non_operational_output

Content that **CANNOT** be executed or followed to perform an action.

### 4.5 semantic_ambiguity

Any condition where a governance artifact permits multiple plausible interpretations of authority, scope, precedence, or required behavior.

Semantic ambiguity **SHALL ALWAYS** be treated as a critical governance failure.

### 4.6 fail_closed

A failure mode in which uncertainty results in rejection, not approximation.

### 4.7 canonical_header

A canonical header is:

The first authority-bearing metadata block in a document

Defines:
anchor_id
anchor_model
anchor_version
scope
status
output_mode
authorship / ownership

Is consumed by:
governance ingestion
validators
audit tooling

Anything that meets this definition MUST be TOML.

---

## 5. Forbidden Language Categories

The following are explicitly forbidden in canonical governance artifacts:

* implied authority ("the system decides")
* inferred intent ("clearly meant", "obviously")
* procedural instruction language ("step-by-step", "do the following")
* trust-based claims ("safe user", "trusted request")

Detection of forbidden language **MUST** trigger semantic ambiguity failure.

---

## 6. Enforcement Requirements

1. All validators **MUST** enforce terminology compliance.
2. Ambiguous or undefined terms **MUST** result in `Semantic Ambiguity` failure.
3. No validator or agent may attempt to reinterpret or "clarify" ambiguous language.

---

## End-of-Document Summary (Normative)

This document defines the complete and binding terminology of the SSWG/MVM governance system. It is the first ingestion layer, the semantic boundary, and the primary defense against ambiguity.

All governance artifacts **MUST** conform exactly to these definitions. Any deviation, ambiguity, or undefined term **SHALL** result in immediate rejection.

This executive-and-summary structure **SHALL be preserved** in all future terminology revisions to ensure clarity, determinism, and auditability.
