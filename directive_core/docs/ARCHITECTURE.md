# === CANONIC LEDGER (TOML) ===
```toml
[anchor]
anchor_id = "architecture"
anchor_model = "sswg+mvm+version"
anchor_version = "1.0.0"
scope = "directive_core/docs"
status = "non-authoritative"
output_mode = "non_operational_output"

owner = [
  "2025© Raven Recordings",
  "Tommy Raven (Thomas Byers)"
]

init_purpose = "Non-authoritative Markdown mirror of the canonical system architecture."
init_authors = ["Tommy Raven"]
```
--- 

# ⚠️ NOTICE — NON-AUTHORITATIVE DOCUMENT

## This document is **NON-AUTHORITATIVE** and **NON-OPERATIONAL**.

It exists solely as a *human-readable mirror* of the canonical architecture definition.

ALL authoritative governance, enforcement, and validation logic is sourced exclusively from:

`directive_core/docs/ARCHITECTURE.toml`

*Markdown documents **SHALL NEVER** be treated as authoritative, contractual, or operational.*


---

## System Architecture (Descriptive Mirror)

> Terminology used herein follows `TERMINOLOGY.toml`, which is authoritative.

---

## Architectural Intent

The `sswg-mvm` system is designed to enforce:

• deterministic artifact generation
• invariant preservation
• bounded recursion
• non-operational outputs only


**The system is not conversational, does not emit procedures, and does not infer intent.**


---

## Constitutional Dependencies

The architecture consumes governance authority from the following canonical documents, in ingestion order:

1. `TERMINOLOGY.toml`
2. `AGENTS.toml`
3. `SSWG_CONSTITUTION.toml`
4. `FORMAT_BOUNDARY_CONTRACT.toml`

If any of these documents are missing, malformed, or out of order, governance validation fails.


---

## Format Boundary Alignment

Authoritative format: TOML only

• **Markdown is NEVER authoritative**
• **YAML is NEVER authoritative**

All machine authority flows through the Format Boundary Contract.


---

## Semantic Ambiguity Alignment

*Semantic ambiguity is treated as a **security vulnerability**.*

The Semantic Ambiguity Gate executes before:

- normalization
- schema validation
- architectural enforcement


On detection of ambiguity:

- processing fails closed
- the artifact is rejected
- the artifact is quarantined



---

## High-Level Architecture Layers

The system consists of the following layers:

1. Artifact generation core
2. Validation and invariant enforcement
3. Bounded recursion engine
4. Evaluation and gating
5. Lineage and evidence management

All layers fail closed and emit evidence.


---

## Component Overview

Major components include:

`generator` — artifact orchestration

`ai_validation` — schema and invariant enforcement

`ai_graph` — dependency graph construction

`ai_recursive` — bounded recursion engine

`ai_evaluation` — deterministic metrics

`ai_memory` — lineage tracking

`ai_visualization` — non-operational exporters

`ai_monitoring` — telemetry and logging

`schemas` — canonical JSON contracts

---

### Artifact Generation Core

The artifact generation core:

- enforces phase ordering
  
- resolves templates deterministically
  
- emits immutable outputs
  
- records lineage
  



---

### Validation & Invariant Enforcement

All artifacts pass through deterministic validation gates:

- JSON Schema validation
- root contract checks
- invariant enforcement


Violations result in fail-closed rejection with a recorded decision trace.


---

### Bounded Recursion Engine

Recursive refinement is strictly bounded:

- explicit termination conditions required
- depth limits enforced
- cost limits enforced
- implicit self-expansion forbidden


Each recursion cycle emits:

- a candidate artifact
- an evaluation result
- an accept/reject decision
- an audit record



---

### Evaluation & Gating

Evaluation gates:

- use deterministic metrics

- compare artifacts via diffs

- apply explicit acceptance criteria


**Unconstrained optimization is forbidden.**


---

### Reference Loop (Pre-Promotion)

A non-phase reference loop runs before promotion.

It emits:

- benchmark evolution summaries

- entropy budget verification

- convergence summaries

- final output snapshots


These artifacts gate promotion without altering the PDL pipeline.


---

### Lineage & Evidence Management

Every artifact is traceable:

- parent-child relationships recorded

- hashes and timestamps preserved

- decision traces stored

- audit bundles supported



---

### Non-Operational Visualization

Visualization outputs are:

- descriptive only

- non-executable

- authority-free

--- 

### Failure Handling

All critical paths **MUST** fail closed.

Failure causes include:

- semantic ambiguity

- schema validation failure

- invariant violation

- recursion limits exceeded

- evaluation gate rejection


**Failures *MUST* emit evidence artifacts.**


---

### Extension Boundaries

Extensions may add:

- artifact templates

- evaluation metrics

- visualization formats


Extensions **MUST NOT**:

- weaken invariants

- bypass validation

- emit operational outputs

- introduce ambiguity



---

## Architectural Guarantees

The architecture guarantees:

- determinism

- bounded recursion

- complete lineage

- auditability


**Formal guarantees are defined in `FORMAL_GUARANTEES.toml`**.


---

## Non-Goals

The system explicitly does not:

- produce operational instructions

- act autonomously

- infer intent

- trust user authority



---

### End-of-Document Summary (Descriptive)

This Markdown document *mirrors* the canonical architecture for human readability only.

All enforcement, validation, and authority derive exclusively from the TOML source.

Any discrepancy between this document and `ARCHITECTURE.toml` **MUST** be resolved in favor of the TOML.
