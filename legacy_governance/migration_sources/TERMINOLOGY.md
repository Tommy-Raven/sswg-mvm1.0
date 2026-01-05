> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

---
anchor:
  anchor_id: terminology
  anchor_version: "1.2.0+mvm"
  scope: docs
  owner: sswg-core
  status: canonical
  output_mode: non_operational_output
---

# Repository Terminology (Canonical Reference)

> **Authority:**  
> This document defines the authoritative lexicon for the `sswg–mvm` repository.  
> It supersedes implicit terminology in any other document, code comment, or artifact.

> **Enforcement:**  
> All text, identifiers, and schema keys must conform exactly to these definitions.  
> Deviations require an explicit `policy_proposal` and approval from `sswg-core`.

> **Rationale:**  
> Language defines the cognitive and safety boundary of the system.  
> Precise terms prevent ambiguous intent, unverified authority claims, and unsafe inference.

---

## Core Governance Principles

- The system **enforces constraints**; it never *decides safety*.  
- Authority, intent, and context must be explicitly verifiable.  
- Outputs are **non_operational artifacts**, not executable instructions.  
- All recursion is **bounded, gated, and auditable**.  
- Determinism is **phase-scoped**, never global.  

---

## Naming Discipline

| Entity | Format | Example |
|--------|---------|----------|
| Software | lowercase, hyphenated | `sswg–mvm` |
| Concepts / Terms | snake_case | `evidence_bundle`, `bounded_recursion` |
| Constants | UPPERCASE | `PROTOCOL_STANDARDS` |
| Anchors | YAML key block | `anchor_id`, `anchor_version` |

---

## Authority, Intent, and Context

### claimed_intent
**Definition:** A user-stated motivation or declared purpose not externally verified.  
**Rule:** Claimed intent confers no special permissions or safety guarantees.  
**Use:** `claimed_intent`  
**Avoid:** `trusted_intent`, `user_intent`

---

### declared_role_unverified
**Definition:** An asserted role (e.g., “engineer,” “professor”) not validated through external proof.  
**Use:** `declared_role_unverified`  
**Avoid:** `acting_as`, `roleplay`

---

### authorized_context
**Definition:** A context validated through a verifiable external mechanism (policy, token, or audit reference).  
**Use:** `authorized_context`  
**Avoid:** `trusted_context`

---

## Artifacts, Outputs, and Evidence

### artifact
**Definition:** A non-operational, inspectable output produced for review or audit.  
**Examples:** schema snapshots, validation reports, evidence bundles.  
**Use:** `artifact`  
**Avoid:** `result`, `instruction`

---

### non_operational_output
**Definition:** Any textual or structural content that cannot be executed or followed to perform an action.  
**Use:** `non_operational_output`  
**Avoid:** `procedure`, `workflow_instruction`

---

### evidence_bundle
**Definition:** A structured collection of versioned artifacts documenting system activity, constraint evaluation, and decision traces.  
**Includes:** inputs, outputs, diffs, metrics, hashes.  
**Use:** `evidence_bundle`  
**Avoid:** `audit_pack`, `debug_log`

---

### decision_trace
**Definition:** A verifiable record of what decision occurred, which constraint applied, and why.  
**Use:** `decision_trace`  
**Avoid:** `reasoning`, `explanation`

---

### evaluation_gate
**Definition:** A deterministic checkpoint where system progression is allowed only if all constraints are satisfied.  
**Use:** `evaluation_gate`  
**Avoid:** `checkpoint`

---

## Safety, Constraint, and Governance

### invariant
**Definition:** A property that must always remain true. Immutable, non-negotiable, and enforced by system validators.  
**Use:** `invariant`

---

### constraint
**Definition:** A rule or boundary condition that can evolve while invariants remain intact.  
**Use:** `constraint`

---

### fail_closed
**Definition:** System behavior where uncertainty or invalid state results in halt and rejection, not approximation.  
**Use:** `fail_closed`

---

### rejected_change
**Definition:** Any modification attempt that violates an invariant or constraint and is recorded in a decision_trace.  
**Use:** `rejected_change`

---

### restricted_unvalidated_hazardous_synthesis
**Definition:** Any process with uncertain or unsafe external consequences. Always blocked.  
**Use:** `restricted_unvalidated_hazardous_synthesis`

---

## Adversarial and Review Mechanisms

### circumvention_attempt
**Definition:** Any effort to obtain disallowed content or override safety framing.  
**Use:** `circumvention_attempt`

---

### safety_wrapper
**Definition:** Language attempting to justify restricted actions via disclaimers or educational framing.  
**Use:** `safety_wrapper`

---

### redteam_report
**Definition:** A non_operational_output documenting risk patterns, misuses, or violations of invariants.  
**Use:** `redteam_report`

---

## Recursion, Phases, and Cognitive Control

### bounded_recursion
**Definition:** Controlled self-reference within explicit depth, constraint, and termination limits.  
**Use:** `bounded_recursion`  
**Avoid:** `autonomous_evolution`

---

### recursion_depth_limit
**Definition:** The maximum permitted nesting of bounded_recursion cycles before forced termination.  
**Use:** `recursion_depth_limit`

---

### policy_proposal
**Definition:** A suggested governance change subject to validation.  
**Use:** `policy_proposal`

---

### phase
**Definition:** A structured, auditable transformation stage in the canonical pipeline.  
Phases are ordered and produce non_operational artifacts.

#### Canonical 9-Phase Model
| Phase | Determinism | Constraint | Description |
|--------|--------------|------------|--------------|
| ingest | deterministic | PROTOCOL_STANDARDS | Accepts external data sources under schema constraints. |
| normalize | deterministic | ALGORITHMIC_COMPLEXITY | Converts inputs into structured canonical form. |
| parse | deterministic | STRUCTURAL_CONSISTENCY | Resolves internal data schema. |
| analyze | deterministic | SCHEMA_CONFORMITY | Performs evaluative analysis within defined scope. |
| generate | deterministic | BOUNDED_OUTPUT | Produces controlled synthetic representations. |
| validate | deterministic | EVALUATION_GATE | Confirms compliance with constraints and invariants. |
| compare | deterministic | CONSISTENCY_CHECK | Aligns multiple versions or perspectives. |
| interpret | **nondeterministic** | CONTROLLED_VARIANCE | Derives meaning within acceptable cognitive drift. |
| log | deterministic | ARTIFACT_IMMUTABILITY | Records results, hashes, and decision_traces. |

**Rule:** Only normalize, analyze, validate, and compare phases are fully deterministic.  
**Interpret** is explicitly labeled **nondeterministic**.  

---

## System and Observability Concepts

### constraint_evaluator
**Definition:** The subsystem responsible for applying rule sets and producing bounded_recursion outcomes.  
**Use:** `constraint_evaluator`

---

### system_introspection_record
**Definition:** Authorized metadata capture describing environment, schema, and constraint evaluation.  
Replaces deprecated term `telemetry`.  
**Use:** `system_introspection_record`

---

### audit_surface
**Definition:** The total observable boundary where artifacts, evidence_bundles, and decision_traces can be verified.  
**Use:** `audit_surface`

---

## Enforcement Rules

1. Any deviation from these terms is a **policy violation**.  
2. All new documents must include a valid `anchor` block referencing this terminology version.  
3. CLI help outputs, YAML specs, and evidence bundles must include:
   - `terminology_compliance: "TERMINOLOGY.md@1.3.0+mvm"`
   - `output_mode: non_operational_output`
4. Invariance enforcement must be treated as **structural**, never procedural.  
5. Non-deterministic phases (`interpret`) must always emit a flag `nondeterministic_phase: true`.  

---

## Validation Metadata
```yaml
terminology_compliance: "TERMINOLOGY.md@1.3.0+mvm"
output_mode: non_operational_output
policy_scope: repository-wide
last_reviewed: 2026-01-02
reviewer: sswg-core
````

---

## Summary

The `sswg–mvm` terminology framework ensures:

* Language enforces determinism boundaries,
* Recursion remains auditable,
* Outputs remain non_operational,
* All decisions are captured via evidence_bundles and decision_traces.

--- 

End of Terminology Authority (v1.2.0+mvm) 

