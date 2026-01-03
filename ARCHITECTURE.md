---
anchor:
  anchor_id: architecture
  anchor_version: "1.2.0"
  scope: docs
  owner: sswg
  status: draft
---

# System Architecture

> **Terminology notice:** All terms in this document are used per `TERMINOLOGY.md`, which is authoritative and enforced.

---

## Architectural Intent

The **sswg-mvm** architecture is designed to enforce **deterministic artifact generation**, **invariant preservation**, and **bounded recursion** under explicit constraints.

The system is not a conversational agent and does not emit operational instructions. Its purpose is to generate **inspectable, non-operational artifacts** with complete lineage and decision traces.

---

## High-Level Architecture

At a high level, the system consists of:

1. **Artifact Generation Core** — produces schema-aligned workflow artifacts  
2. **Validation & Invariant Enforcement** — enforces non-negotiable conditions  
3. **Bounded Recursion Engine** — permits controlled refinement  
4. **Evaluation & Gating** — determines admissibility of changes  
5. **Lineage & Evidence Management** — records traceability and audit artifacts  

Each layer is fail-closed and produces evidence.

---

## Component Overview

sswg-mvm/ ├── generator/            # Artifact generation orchestration ├── ai_validation/        # Schema and invariant enforcement ├── ai_graph/             # Dependency graph construction ├── ai_recursive/         # Bounded recursion engine ├── ai_evaluation/        # Deterministic quality metrics ├── ai_memory/            # Lineage and version tracking ├── ai_visualization/     # Non-operational diagram exporters ├── ai_monitoring/        # Telemetry and logging ├── data/templates/       # Seed non-operational artifacts └── schemas/              # Canonical JSON schemas and contracts

---

## Artifact Generation Core

The artifact generation core orchestrates the canonical pipeline and emits **schema-aligned workflow artifacts**.

Responsibilities:
- Apply canonical phase ordering
- Resolve template inputs
- Produce initial artifacts for validation

Outputs are immutable snapshots recorded in lineage storage.

---

## Validation & Invariant Enforcement

All artifacts pass through deterministic validation gates.

This layer enforces:
- JSON Schema compliance
- Root contract adherence
- Invariant preservation

Schema validation is centralized in `ai_validation/schema_core.py` and shared across validation entrypoints.

Violations result in **fail-closed rejection** and a recorded decision trace.

---

## Bounded Recursion Engine

Recursive refinement is managed by the bounded recursion engine.

Characteristics:
- Explicit termination conditions
- Hard limits on depth and cost
- No implicit self-expansion

Each recursion cycle produces:
- a candidate artifact
- an evaluation result
- an acceptance or rejection decision
- an audit record

---

## Evaluation & Gating

Evaluation gates determine whether candidate artifacts may replace their predecessors.

Properties:
- Deterministic metrics
- Diff-based comparison
- Explicit acceptance criteria

Gates do not optimize freely; they enforce constraints.

---

## Reference Loop (Pre-Promotion Control)

The `run_reference_loop` control loop (implemented in `generator/reference_loop.py`) runs **outside** the 9-phase PDL pipeline. It is explicitly **non-phase**, yet **promotion-gating**: its outcomes must be satisfied before a run can be promoted.

This loop contributes pre-promotion evidence to audit bundles, including:
- benchmark evolution summaries (verity, entropy, determinism trajectories)
- entropy budget verification summaries
- convergence summaries and the final run output snapshot

These artifacts are used to validate promotion readiness without collapsing or replacing any canonical phase in the PDL pipeline.

---

## Lineage & Evidence Management

Every artifact is versioned and traceable.

The lineage system records:
- parent-child relationships
- hashes and timestamps
- decision traces
- associated evidence bundles

This ensures reproducibility and auditability.

---

## Non-Operational Visualization

Visualization components export diagrams (e.g., DAGs) as **non-operational representations**.

These outputs are descriptive only and are never executable.

---

## Failure Handling

All critical paths are **fail-closed**.

Examples:
- schema validation failure
- invariant violation
- recursion limit exceeded
- evaluation gate rejection

Failures emit artifacts documenting cause and context.

---

## Extension Boundaries

Extensions may:
- add new artifact templates
- introduce additional evaluation metrics
- add visualization formats

Extensions must not:
- weaken invariants
- bypass validation gates
- introduce operational outputs

---

## Architectural Guarantees

The architecture guarantees:
- deterministic behavior under identical inputs
- bounded recursion
- complete lineage tracking
- auditable decision traces

Formal guarantees are documented in `docs/FORMAL_GUARANTEES.md`.

---

## Non-Goals

The system explicitly does not:
- provide non-operational outputs framed as step sequences
- act autonomously outside enforced bounds
- infer or trust user authority or intent
- generate operational procedures

---

## Summary

The **sswg-mvm** architecture is a governance-first substrate for recursive artifact generation. Its design prioritizes control, auditability, and safety over flexibility or convenience.
