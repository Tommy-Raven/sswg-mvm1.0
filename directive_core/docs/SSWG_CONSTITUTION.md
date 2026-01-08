# Canonic Ledger

```yaml
anchor:
  anchor_id: "sswg_constitution"
  anchor_model: "sswg+mvm+version"
  anchor_version: "1.0.0"
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

--- 

## Executive Summary

This Constitution is the **highest-order normative authority** of the SSWG/MVM governance system. It defines the foundational principles, authority boundaries, and enforcement guarantees that govern all directive definitions, schemas, validators, and governance documentation contained within `directive_core/`.

This document establishes a **single, non-negotiable source of governance truth**. All other governance artifacts derive their authority from this Constitution and are subordinate to it. Where ambiguity, conflict, or omission exists elsewhere, this document SHALL control.

Effective at `anchor_version: 1.0.0`, this Constitution governs a system in which governance is **machine-enforced, fail-closed, and auditable by design**. Prior materials are preserved solely for historical context and confer no authority.

---

## 1. Purpose and Authority

### 1.1 Supreme Authority

1. This document **SHALL ALWAYS** be the highest-order normative authority within `directive_core/`.
2. All directive definitions, schemas, governance documents, validators, and enforcement mechanisms **MUST FIRST** conform to this Constitution.
3. In the event of conflict between this Constitution and any other document, schema, code path, or tool behavior, this Constitution **SHALL ALWAYS** take precedence.
4. This Constitution **SHALL NEVER** be overridden, bypassed, or weakened by project code, tooling, runtime behavior, or contributor intent.

### 1.2 Source of Legitimacy

Governance legitimacy within the SSWG/MVM system is derived exclusively from:

* explicit constitutional declaration,
* deterministic ingestion order,
* validator-enforced compliance.

No implicit authority, convention, or historical usage SHALL confer governance power.

---

## 2. Scope of Governance

### 2.1 Governed Domains

This Constitution **ALWAYS** governs the following domains:

1. Directive definitions
2. Directive schemas
3. Governance documentation
4. Validation and enforcement logic
5. Audit artifacts and evidence bundles

### 2.2 Excluded Domains

This Constitution **SHALL NEVER** govern:

1. Application or business logic
2. Runtime execution outside `directive_core/`
3. Non-governance experimentation or sandbox code

---

## 3. Canonical Governance Model

### 3.1 Canonical Encoding

All canonical governance documents **MUST** declare their identity using the following anchor encoding:

```yaml
anchor_model: "sswg+mvm+version"
anchor_version: "1.0.0"
```

This encoding establishes the governance system and the semantic baseline version independently. Any deviation **SHALL** result in validation failure.

### 3.2 Baseline Declaration

The value `anchor_version: 1.0.0` denotes the **first enforced governance baseline**, corresponding to the completion of Phase 2 governance enforcement.

This baseline marks the transition from documented intent to enforced authority.

---

## 4. Canonical Governance Ingestion Order and Precedence

### 4.1 Mandatory Ingestion Order

Governance documents **MUST** be ingested in the following exact order:

1. `TERMINOLOGY.md`
2. `SSWG_CONSTITUTION.md`
3. `AGENTS.md`
4. `ARCHITECTURE.md`
5. `FORMAL_GUARANTEES.md`
6. `REFERENCES.md`
7. `deprecated_nomenclature.md`

Missing, malformed, or out-of-order ledger documents **SHALL** cause governance validation failure.

### 4.2 Precedence Rules

* Terminology definitions are binding across all documents.
* Constitutional rules override all subordinate governance materials.
* Later documents MAY refine but SHALL NOT contradict earlier ones.

---

## 5. Enforcement and Fail-Closed Guarantees

# Semantic Ambiguity Gate (Pre-Ingestion, Mandatory)

## Principle

## SSWG **SHALL** treat ambiguity as a **security vulnerability**, not a stylistic defect.

#### Any semantic ambiguity in a governance artifact **MUST** be treated as a critical failure condition.

### Execution Order

The Semantic Ambiguity Gate **MUST** execute **before**:

1. governance ingestion order enforcement,
2. anchor validation,
3. constitution precedence checks,
4. any additional governance or schema validation.

If the Semantic Ambiguity Gate fails, **NO OTHER GOVERNANCE VALIDATION MAY RUN**.

### Enforcement

On detection of semantic ambiguity, validators **MUST**:

1. hard-fail in fail-closed mode,
2. emit the error label **`Semantic Ambiguity`**,
3. record the affected path in an append-only quarantine registry,
4. automatically **exile** the ambiguous artifact from the ingestion candidate set.

Exiled artifacts **SHALL NOT** contribute to governance meaning, precedence, or downstream validation.

### Remediation Doctrine

The only permitted remediation path is:

1. immediate rejection,
2. explicit re-authoring to remove ambiguity,
3. terminology refinement to prevent recurrence,
4. retraining/behavioral refinement of semantic modeling tools where applicable,
5. re-ingestion under full validation.

Ambiguity **MUST** be eradicated immediately to prevent propagation.

#### All constitutional rules **MUST** be enforced by validators.
#### Governance enforcement **SHALL** operate in fail-closed mode.
#### Any uncertainty, ambiguity, or validation error **MUST** result in rejection, not approximation.

** No discretionary bypass is permitted.**
No human intervention may circumvent this immutability except for controlled experimentals.

---

## 6. Naming Status (Canonical)

Only **SSWG/MVM** (governance mindset and ethos) and **sswg-mvm** (software implementation) are canonical identifiers.

All other naming variants are deprecated and **SHALL NOT** be used in canonical governance documents.

Deprecated identifiers are documented in [`deprecated_nomenclature.md`](./deprecated_nomenclature.md) and are retained for historical traceability only.

---

## 7. Evolution and Change Control

1. Governance evolution **MUST** occur through explicit versioned changes.
2. Backward traceability to `anchor_version: 1.0.0` **MUST** be preserved.
3. Silent modification, reinterpretation, or retroactive alteration of governance meaning is forbidden.

---

## End-of-Document Summary (Normative)

This Constitution establishes the absolute authority, scope, and enforcement guarantees of the SSWG/MVM governance system. It defines a single canonical baseline (`anchor_version: 1.0.0`), mandates deterministic ingestion and precedence rules, and requires machine-enforced, fail-closed compliance.

All governance documents, validators, and future amendments **MUST** conform to this Constitution. Any artifact that violates its requirements is non-canonical by definition and **SHALL** be rejected.

This executive-and-summary structure **SHALL be replicated** in all future constitutional or governance-defining documents to ensure clarity, auditability, and closure.
