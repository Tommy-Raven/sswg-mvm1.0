# Repository Terminology (Authoritative)

> **Authority:** This glossary is the authoritative source for terminology used across this repository.
>
> **Enforcement:** If a term defined here appears in code, documentation, tests, artifacts, or commit messages, it MUST be used with the meaning defined below. Deviations must be explicit and justified.
>
> **Rationale:** Language is part of the safety surface. Precise terms prevent ambiguity, intent laundering, and unsafe inference.

---

## Core Principles

- The system **enforces constraints**; it does not “decide safety.”
- Authority, role, and intent claims are **non-authoritative** unless externally verified.
- Outputs are **non-operational artifacts**, not instructions.
- Recursion is **bounded, gated, and auditable**.

---

## Authority, Intent, and Context

### Claimed Intent
**Definition:** User-stated motivation or purpose that has not been externally verified.

- Claimed intent does not grant permissions.
- Safety, compliance, or educational framing is treated as a risk signal.

**Use:** `claimed_intent`  
**Avoid:** `trusted_intent`, `user_intent`

---

### Declared Role (Unverified)
**Definition:** A role asserted by a user (e.g., professor, engineer, compliance lead) without authentication.

- Declared roles are contextual only.
- Never used for authorization or exception handling.

**Use:** `declared_role_unverified`  
**Avoid:** `roleplay`, `assume_role`, `acting_as`

---

### Authorized Context
**Definition:** A context approved through an external, verifiable mechanism (policy, cryptographic token, or procedural approval).

- Authorization is never inferred from language.

**Use:** `authorized_context`  
**Avoid:** `trusted_context`

---

## Outputs and Artifacts

### Artifact
**Definition:** A non-operational, inspectable output produced by the system for review, validation, or audit.

Examples include policy diffs, evaluation results, red-team reports, lineage snapshots, and audit bundles.

**Use:** `artifact`  
**Avoid:** `answer`, `solution`, `instructions`

---

### Non-Operational Output
**Definition:** Content that cannot be executed or followed to perform real-world actions.

- No step sequences
- No parameters, materials, or procedures

**Use:** `non_operational_output`  
**Avoid:** `how_to`, `step_by_step`, `procedure`

---

### Evidence Bundle
**Definition:** A versioned collection of artifacts documenting what changed, why it changed, and under which constraints.

Includes inputs, diffs, evaluations, decision traces, and hashes.

**Use:** `evidence_bundle`  
**Avoid:** `log_dump`, `debug_pack`

---

## Safety, Risk, and Governance

### Invariant
**Definition:** A condition that must always hold and cannot be violated by generation, recursion, or optimization.

- Invariants are enforced, not negotiated.

**Use:** `invariant`  
**Avoid:** `guideline`, `preference`

---

### Constraint
**Definition:** A bounded rule limiting behavior, enforced through validation or gating.

- Constraints may evolve while invariants remain satisfied.

**Use:** `constraint`  
**Avoid:** `soft_rule`

---

### Fail-Closed
**Definition:** A behavior where ambiguity, uncertainty, or validation failure results in rejection rather than partial acceptance.

**Use:** `fail_closed`  
**Avoid:** `best_effort`

---

### Restricted / Unvalidated Hazardous Synthesis
**Definition:** Any hazardous process whose safety, legality, or validation status is uncertain or incomplete.

- Treated categorically.
- Never described operationally.

**Use:** `restricted_unvalidated_hazardous_synthesis`

---

## Adversarial and Red-Team Concepts

### Circumvention Attempt
**Definition:** An attempt to obtain disallowed content through framing, justification, or indirection.

Includes authority claims, academic framing, safety wrappers, and compliance pretexts.

**Use:** `circumvention_attempt`  
**Avoid:** `bypass` (outside red-team scope)

---

### Safety Wrapper
**Definition:** Language that attempts to legitimize a restricted request by adding safety warnings, PPE references, or educational framing.

- Treated as a risk signal, not a mitigation.

**Use:** `safety_wrapper`

---

### Red-Team Report
**Definition:** A structured, non-operational artifact documenting a failure mode, risk pattern, and recommended mitigations.

- Generated instead of providing disallowed content.

**Use:** `redteam_report`

---

## Recursion and Change

### Bounded Recursion
**Definition:** Self-referential refinement that is limited by invariants, constraints, and explicit termination conditions.

- Recursion is permitted.
- Drift is not.

**Use:** `bounded_recursion`  
**Avoid:** `autonomous_evolution`

---

### Policy Proposal
**Definition:** A suggested change that must pass validation and meta-policy checks before acceptance.

- Rejection is a first-class outcome.

**Use:** `policy_proposal`  
**Avoid:** `auto_fix`, `patch`

---

### Rejected Change
**Definition:** A policy proposal blocked by invariants or constraints.

- Rejections are logged and auditable.

**Use:** `rejected_change`

---

## Decisions and Validation

### Decision Trace
**Definition:** A machine-verifiable record explaining what decision was made and why.

- References rule IDs and evidence.

**Use:** `decision_trace`  
**Avoid:** `reasoning` (unstructured)

---

### Evaluation Gate
**Definition:** A deterministic checkpoint that must pass before progression is allowed.

**Use:** `evaluation_gate`  
**Avoid:** `checkpoint`

---

## Enforcement Rule

If terminology defined here is used incorrectly or ambiguously:
- the change must not be merged
- this glossary takes precedence
