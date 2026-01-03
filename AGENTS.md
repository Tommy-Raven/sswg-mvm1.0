---
anchor:
  anchor_id: agents
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# AGENTS.md — sswg / mvm Compliance Operations Manual (v0.0.9mvm)

This document defines **mandatory** behaviors for all contributors, automation agents, CI runners, and tooling that touch this repository.

Language is intentionally normative (**MUST / SHALL / SHOULD**) to function as an enforceable production standard.

> **Terminology notice:** Terms are used per `TERMINOLOGY.md`, which is authoritative. Where this document uses legacy repo terms (e.g., “artifact”), those are interpreted as defined in the glossary.

---

## 0) Agent Guidelines (Root Scope) — Mandatory Operating Rules

- This repository **MUST** be treated as read-only for QA unless a task explicitly permits edits or test execution.
- Agents **MUST** use `rg` for searching and **MUST NOT** use `ls -R` or `grep -R`.
- Agents **MUST NOT** validate commands with `echo $?`; agents **MUST** rely on actual command outputs.
- When reporting issues or improvements, agents **MUST** append a `task-stub` block immediately after each issue description with clear, actionable steps.
- Final responses **MUST** be concise, **MUST** include citations where relevant, and **MUST** prefix any test/check commands with emojis:
  - ✅ pass
  - ⚠️ warning/limitation
  - ❌ fail
- For frontend visual changes, agents **MUST** capture screenshots via the browser tool and **MUST** cite the artifact.
- Agents **MUST** honor instruction precedence: system > developer > user > AGENTS, with deeper `AGENTS.md` overriding parent scopes.
- If any placeholders or TODOs remain in the final diff, agents **MUST** include a **Notes** section after **Testing**; agents **MUST** omit the section otherwise.
- When changes are made, agents **MUST** commit them, then **MUST** invoke `make_pr` with an appropriate title and body; agents **MUST NOT** leave committed changes without calling `make_pr`, and agents **MUST NOT** call `make_pr` without commits.

---

## 0.1 Terminology Authority & Enforcement (Mandatory)

`TERMINOLOGY.md` is the authoritative source of meaning for all terms used in this repository.

All agents (human or automated) **MUST** treat terminology definitions as normative, not descriptive.

If a term is defined in `TERMINOLOGY.md`, its definition **MUST** be used consistently across:

- documentation
- code comments
- schemas
- logs
- CLI output
- audit bundles

If a concept is not defined in `TERMINOLOGY.md`, agents **MUST NOT**:

- introduce it implicitly,
- substitute a colloquial synonym,
- or infer meaning from common usage.

Ambiguous language **MUST** be rewritten to use glossary-defined terms.

Failure to comply with terminology authority is a governance violation.

---

## 1) Naming Discipline (Required)

- **sswg / mvm / nvm** refer to software components / behaviors (lowercase).
- **SSWG / MVM / NVM** refer to governance mindsets / mental models (uppercase).

Any documentation, logs, schemas, or code that violates this naming discipline **SHOULD** be corrected during the same change set.

---

## 1.1 Forbidden and Restricted Language (Terminology Guardrails)

The following categories of language are restricted and **MUST NOT** appear unless explicitly defined and scoped in `TERMINOLOGY.md`:

- implied agency (e.g., “the system decides”, “the model chooses”)
- trusted intent (e.g., “safe user”, “authorized request”)
- operational instruction language (e.g., “step-by-step”, “procedure”, “how to perform”)
- implicit permission language (e.g., “allowed to”, “can be used for” without scope)

If such language appears, agents **MUST**:

- flag it as a defect, or
- rewrite it using approved glossary terms (e.g., `descriptive_output`, `non_authoritative_signal`, `gate_failure`).

---

## 2) Release Families + Version Semantics (Required)

This repo distinguishes **release families**. Agents **MUST** treat these as authoritative taxonomy when labeling artifacts, tags, and docs.

### 2.1 sswg (stable line)
- `sswg vX.Y.Z` denotes a stable release line.
- A stable `sswg` release **SHALL** be treated as “no known blocking issues” at release time and **MUST** satisfy all immutable gates in this document.

### 2.2 sswg-exp (experimental line)
- `sswg-exp vV.X.Y` denotes an experimental release.
- `V` denotes the stable release family being experimented against (anchor family).
- `.X.Y` denotes what is being experimented on.
- Experimental releases **MUST** still satisfy the canonical 9-phase pipeline contract unless explicitly scoped as sandbox-only and barred from promotion.

### 2.3 sswg-trs (transitive-deterministic line)
- `sswg-trs vN.X.Y` denotes a stable deterministic release line.
- `sswg-trs vN.*.*` **MUST** be deterministic and backward-compatible across all models up to that major family `vN` and earlier (as declared by compatibility policy).
- Any claim of trs determinism/back-compat **MUST** be proven by reproducibility + replay + compatibility evidence gates.

### 2.4 mvm (minimum viable model line)
- `mvm` defines the **minimum viable model**: the minimum acceptable pipeline completeness for `sswg` software.
- `mvm` is a **minimum skeletal pipeline structure** that **MUST NOT** return errors under its declared scope, but **MAY** contain small bugs that do not break gating invariants or determinism contracts where required.
- `mvm` **MUST** always enforce the canonical 9-phase pipeline and required validation gates in this document.

---

## 3) Canonical Mission (Non-Negotiable)

### 3.1 sswg mandate
sswg **MUST** enforce a **phase-driven**, **audit-ready**, **9-phase** pipeline that yields deterministic measurement outputs where required.

### 3.2 mvm mandate (minimum viable model)
mvm defines the **minimum viable model**, the minimum acceptable pipeline completeness for sswg software. Workflows and tooling are invalid unless the full **9-phase** pipeline is supported and enforced at the mvm level.

---

## 4) Global Canonic mvm Requirements (Immutable Gates)

This section defines the global canonic **minimum viable model (mvm)** requirements as **immutable gates**. These gates are binding for all work, including `sswg`, `sswg-exp` (unless sandbox-barred), and `sswg-trs`. Any violation **MUST** hard-fail execution and **MUST** block promotion.

### 4.1 Immutable gate: 9-phase availability (full_9_phase)
- The pipeline **MUST** support the canonical set `full_9_phase`.
- The pipeline phases **MUST** exist and be enforceable in order:
  - `ingest`
  - `normalize`
  - `parse`
  - `analyze`
  - `generate`
  - `validate`
  - `compare`
  - `interpret`
  - `log`

### 4.2 Immutable gate: phase separation enforcement
- Phase separation **MUST** be enforced.
- Each phase **MUST** be declared explicitly and validated against its phase-specific schema.
- Phase behaviors **MUST NOT** be collapsed.

### 4.3 Immutable gate: minimum artifacts present
The repo **MUST** include, at minimum:
- `schemas/`
- `pdl/`
- validation entrypoints
- logging outputs

If any minimum artifact is missing, execution **MUST** stop and emit `Type: reproducibility_failure` or `Type: io_failure` (as appropriate).

### 4.4 Immutable gate: required schema validation coverage
The system **MUST** validate:
- the PDL phase-set schema
- all phase-level schemas

At minimum, the following must exist and be valid:
- `schemas/pdl.json` (wrapper)
- `schemas/pdl-phase-set.json`
- `schemas/pdl-phases/_common.json`
- `schemas/pdl-phases/{ingest,normalize,parse,analyze,generate,validate,compare,interpret,log}.json`

### 4.5 Immutable gate: deterministic phases
Determinism is **required** for phases:
- `normalize`
- `analyze`
- `validate`
- `compare`

If determinism is violated in any required phase, execution **MUST** halt and the failing phase **MUST** emit:
- `Type: deterministic_failure`

### 4.6 Immutable gate: audit-ready outputs
Audit readiness **MUST** include support for:
- bijective identifiers (where measurement keys are used)
- replayable runs (deterministic phases reproducible from logged inputs)
- delta comparisons (deterministic compare artifacts)

Failure to satisfy audit-ready output requirements **MUST** block promotion and **MUST** emit the appropriate failure label type.

### 4.7 Immutable gate: enforcement behavior
If any immutable mvm gate is violated:
- execution **MUST** halt (`failure_behavior: stop_execution`)
- the failing phase **MUST** emit a required failure label
- when the violation is deterministic, the label **MUST** include:
  - `Type: deterministic_failure`

---

## 5) Canonical 9-Phase Pipeline (Full Set, Ordered, Separated)

All runs, workflows, and artifacts **MUST** conform to the canonical phase order:

1. `ingest`
2. `normalize`
3. `parse`
4. `analyze`
5. `generate`
6. `validate`
7. `compare`
8. `interpret`
9. `log`

### 5.1 Determinism requirements
Determinism is **required** for phases:
- `normalize`
- `analyze`
- `validate`
- `compare`

Interpretation is explicitly **nondeterministic** and **MUST** be labeled as such (see §10.4).

---

## 6) Global Canon Requirements (Apply to All Work)

### 6.1 Canonic anchoring (required metadata)
Every artifact produced or modified in this repo **MUST** have a canonical anchor containing:

- `anchor_id`
- `anchor_version`
- `scope`
- `owner`
- `status` ∈ {`draft`, `sandbox`, `canonical`, `archived`}

If an artifact format cannot embed this metadata inline, the metadata **MUST** exist as a colocated sidecar file or registry entry under an agreed canonical index.

### 6.2 Immutability of canon
- Once `status: canonical`, the anchored artifact **MUST** be immutable.
- Canonical changes **MUST** occur via delta overlays only (see §6.3).
- Any direct modification to a canonical anchor **MUST** hard-fail.

### 6.3 Cross-schema delta overlays (mandatory evolution mechanism)
All schema and governance evolution **MUST** be expressed as overlays, not destructive rewrites.

Each overlay **MUST** declare:
- `base_schema_ref` (immutable pointer)
- `overlay_id`, `overlay_version`
- explicit field-level operations: `add` / `override` / `deprecate`
- precedence rules (overlay wins **only** within declared scope)
- compatibility statement: `backward` / `forward` / `breaking`

Promotion **MUST** be blocked if:
- an overlay introduces ambiguous interpretation, OR
- an overlay breaks declared compatibility without a migration plan.

---

## 6.4 Terminology Drift Detection (Required)

Any change that introduces or modifies language **MUST** be evaluated for terminology drift.

Terminology drift is defined as:

- use of undefined terms,
- redefinition of glossary terms,
- or semantic weakening of established definitions.

Terminology drift **MUST** be treated as a regression.

Regressions **MUST** block promotion until corrected.

Agents **SHOULD** prefer refactoring language over adding new terms.

---

## 7) Canonical Schema Contracts (PDL)

### 7.1 Required schemas
The canonical PDL enforcement is:

- `schemas/pdl.json` (wrapper)
  - delegates to `schemas/pdl-phase-set.json`
  - which enforces the 9-phase ordered prefixItems set
- `schemas/pdl-phase-set.json`
- `schemas/pdl-phases/_common.json`
- `schemas/pdl-phases/{ingest,normalize,parse,analyze,generate,validate,compare,interpret,log}.json`

### 7.2 PDL validity requirement
- Any PDL document claiming `pipeline_profile: full_9_phase` **MUST** validate against `schemas/pdl.json`.
- A PDL document **MUST** contain exactly 9 phases in correct order (`prefixItems` enforcement).
- `items: false` is authoritative: additional phases or reordering **MUST** fail validation.

### 7.3 Handler + IO requirements (PDL contract)
- Each phase **MUST** include:
  - `name`, `type`, `enabled`, `description`, `inputs`, `outputs`, `handler`
- Each `inputs[]` / `outputs[]` entry **MUST** conform to `_common.json#/$defs/io_item`.
- `id` fields **MUST** match: `^[a-z][a-z0-9_\\-]*$`
- Phase schema constraints are authoritative. If a phase schema requires a constraint field, it **MUST** be present and correct.

### 7.4 Phase-specific constraint invariants (enforced by schema)
Agents **MUST** ensure the following per-phase constraints remain satisfied:

- `ingest`: `no_interpretation: true`, `no_mutation_of_canonical: true`
- `normalize`: `deterministic_required: true`, `alignment_rules_required: true`
- `parse`: `schema_binding_required: true`, `no_generation: true`
- `analyze`: `deterministic_required: true`, `no_generative_tools_for_measurement: true` (bijective IDs when applicable)
- `generate`: `outputs_must_be_declarative: true`, `no_measurement_keys_generated_stochastically: true`
- `validate`: `schema_validation_required: true`, `invariants_required: true` (bijectivity checks when applicable)
- `compare`: `deterministic_required: true`, `overlap_metrics_allowed ⊆ {iou, jaccard}`
- `interpret`: `must_reference_measured_artifacts: true`, `output_must_be_labeled_nondeterministic: true`
- `log`: `run_id_required: true`, `inputs_hash_required: true`, `phase_status_required: true`

---

## 8) Repository Layer Policy (Immutable vs Additive)

### 8.1 Canonical layers (immutable)
The following directories are canonical layers and **MUST** be treated as immutable in production:

- `generator/`
- `cli/`
- `pdl/`
- `reproducibility/`

### 8.2 Generated layers (additive-only)
The following directories are generated layers and **MUST** be additive-only:

- `artifacts/`
- `data/`
- `docs/`

---

## 9) Validation Gates (Promotion Blocking, Required)

Promotion, merge, release, or “canonical” marking **MUST** be blocked unless all required gates pass:

1. `schema_validation`
2. `phase_schema_validation`
3. `invariants_validation`
4. `reproducibility_validation`

A gate failure **MUST**:
- emit the correct failure label, and
- stop execution.

---

## 9.1 Terminology Compliance Gate (Promotion Blocking)

Promotion, release, or canonical marking **MUST** be blocked if terminology compliance fails.

Terminology compliance includes:

- alignment with `TERMINOLOGY.md`,
- absence of forbidden language (§1.1),
- and consistent use of defined terms.

Tooling **MAY** automate this check.

Manual review **MUST** default to the most restrictive interpretation.

Failure **MUST** be treated as a governance failure, not a stylistic issue.

---

## 10) Failure Labeling Standard (Hard-Fail, Typed, Auditable)

### 10.1 Required failure label fields
On any failure, the failing phase **MUST** emit a failure label containing:

- `Type`
- `message`
- `phase_id`

### 10.2 Allowed failure types
`Type` **MUST** be one of:
- `deterministic_failure`
- `schema_failure`
- `io_failure`
- `tool_mismatch`
- `reproducibility_failure`

### 10.3 Hard-fail policy
- When any required invariant fails, the phase **MUST** emit a failure label and **MUST** hard-fail execution immediately.
- “Soft failures,” “warnings-only,” or “continue on error” behavior **MUST NOT** occur for required invariants.

### 10.4 Interpret phase labeling (nondeterministic)
- `interpret` outputs **MUST** be labeled nondeterministic and **MUST** reference measured artifacts only.
- `interpret` **MUST NOT** mutate measurement outputs or canonical anchors.

### 10.5 Entropy budget violations (promotion-gating)
- Entropy budget violations **MUST** be treated as promotion-gating hard failures.
- The owning phase is `validate`.
- The failure label **MUST** include:
  - `Type: deterministic_failure`
  - `phase_id: validate`
  - a deterministic message such as `entropy_budget_exceeded`.

---

## 11) Validator Operations (Required Tooling + Exact Actions)

### 11.1 Required validator entrypoint
The repo **MUST** provide a validator module capable of:
- loading `schemas/pdl.json` (wrapper → phase set),
- resolving local `$ref` across `schemas/pdl-phases/*`,
- validating PDL YAML/JSON,
- emitting correctly typed failure labels,
- exiting non-zero on failure.

### 11.2 Phase ownership of schema validation failures
Schema validation failures **MUST** be labeled:
- `Type: schema_failure`
- `phase_id: validate`

### 11.3 Required pre-run action
Agents and CI **MUST** validate any PDL before execution.

✅ `python -m generator.pdl_validator pdl/example_full_9_phase.yaml schemas`

---

## 12) Compare Phase Requirements (Deterministic Deltas)

- `compare` **MUST** be deterministic.
- If overlap metrics are used, they **MUST** be restricted to:
  - `iou`
  - `jaccard`

---

## 13) Log Phase Requirements (Audit-Ready Output)

The `log` phase **MUST** emit audit-ready outputs including:
- `run_id`
- input hashes
- per-phase status
- references to PDL, schema versions, overlay versions, and failure labels.

---

## 14) Agent Responsibilities (Exact Actions for Compliance)

All agents (human or automated) working in this repo **MUST** follow this sequence whenever they create/modify pipeline artifacts.

### 14.1 Before making changes
1. **MUST** identify affected phases.
2. **MUST** identify touched layers (canonical vs generated).
3. **MUST** use overlays by default; base rewrites are disallowed unless explicitly authorized.

### 14.2 While making changes
1. **MUST** preserve phase separation and required constraints.
2. **MUST** preserve determinism requirements.
3. **MUST** ensure canonical anchors exist.
4. **MUST** ensure failures are labeled and hard-fail.

### 14.3 After making changes (required checks)
1. **MUST** validate PDL against `schemas/pdl.json`.
2. **MUST** ensure phase schemas validate.
3. **MUST** ensure gates pass before promotion.
4. **MUST** ensure audit-ready log outputs exist.
5. **MUST** provide reproducibility notes for replay.

---

## 15) Prohibited Behaviors (Hard Stops)

- Changing the 9-phase set, order, or separation.
- Introducing nondeterminism into required deterministic phases.
- Using generative tooling to generate measurement keys.
- Directly mutating canonical anchors.
- Violating additive-only layer constraints.
- Emitting untyped failures or failing silently.
- Violating root-scope agent rules (§0), including prohibited search commands and PR/commit flow.

---

## 16) Minimal Acceptance Criteria (Release/Promotion Readiness)

A change set is not promotion-ready unless:

- PDL validation passes (`schemas/pdl.json` wrapper).
- Phase schemas pass for all 9 phases.
- Determinism checks pass for required phases.
- Compare outputs are deterministic and metric-compliant.
- Interpret outputs are measured-only and labeled nondeterministic.
- Log outputs include run id, input hashes, statuses, and references.
- Failure labeling is correct under intentional violation tests.

---

## 17) Enforcement Policy (Authority)

- `sswg.yaml` has highest precedence; violation policy is `hard_fail`.
- `mvm.yaml` defines minimum viable model completeness; missing requirements invalidate workflows.

Agents **MUST** treat these as authoritative constraints. No bypasses are permitted.

---

## 18) Quick Reference: Required Files (Minimum Set)

Agents **MUST** verify presence and correctness of:

- `sswg.yaml`
- `mvm.yaml`
- `schemas/pdl.json`
- `schemas/pdl-phase-set.json`
- `schemas/pdl-phases/_common.json`
- `schemas/pdl-phases/*.json` (9 files)
- `generator/pdl_validator.py`
- `pdl/example_full_9_phase.yaml`

Any missing file in the minimum set **MUST** stop execution and **MUST** emit:
- `Type: reproducibility_failure` (environment cannot be reconstructed), or
- `Type: io_failure` (missing/unreadable path),
with `phase_id: validate` when discovered during validation.


19) Nested Scope Rules (Hierarchical Enforcement & Override Semantics)

## 19) Nested Scope Rules (Hierarchical Enforcement & Override Semantics)

This section defines how **nested AGENTS scopes** operate across the repository and how conflicts are resolved.

Nested scope rules are **mandatory** and **enforceable**.

---

## 19.1 Scope Hierarchy (Authoritative Order)

Instruction precedence within this repository is strictly ordered as follows:

1. **System instructions** (platform / execution environment)
2. **Developer instructions** (repo-wide, out-of-band controls)
3. **User instructions** (task-level intent)
4. **AGENTS.md (root)** — this document
5. **Nested AGENTS.md** (directory-scoped)
6. **Inline scope directives** (explicit, file-local)

Lower-numbered scopes **always override** higher-numbered scopes.

No scope may weaken or bypass constraints imposed by a higher-precedence scope.

---

## 19.2 Definition of a Nested Scope

A **nested scope** is introduced by the presence of an `AGENTS.md` file located in a subdirectory.

Example:

/AGENTS.md                → root scope /generator/AGENTS.md     → generator scope /schemas/AGENTS.md       → schema scope /docs/AGENTS.md          → documentation scope

Each nested `AGENTS.md` applies **only** to:
- files within the same directory, and
- all descendant subdirectories **unless overridden again**.

---

## 19.3 Allowed Behavior of Nested Scopes

A nested scope **MAY**:

- Add **additional constraints**
- Narrow permissions
- Introduce stricter validation, formatting, or tooling rules
- Specialize responsibilities for that directory
- Declare directory-specific invariants or gates

A nested scope **MUST NOT**:

- Weaken root-scope requirements
- Relax invariants, determinism, or audit requirements
- Redefine canonical phase behavior
- Introduce operational outputs
- Override failure labeling standards
- Bypass validation gates

If a nested scope conflicts with a parent scope, the **more restrictive interpretation MUST be applied**.

---

## 19.4 Invariant Inheritance Rule (Non-Negotiable)

All invariants defined at higher scopes are **automatically inherited** by nested scopes.

- Nested scopes **cannot opt out** of invariants.
- Nested scopes **cannot redefine invariants**.
- Nested scopes may only **add invariants**, never remove them.

Violation of an inherited invariant **MUST** hard-fail execution.

---

## 19.5 Constraint Narrowing Rule

Constraints may be **narrowed** but never broadened.

Example:
- Root scope: “Phase X MUST be deterministic”
- Nested scope: “Phase X MUST be deterministic AND use algorithm Y”

Valid.

Example (invalid):
- Root scope: “Phase X MUST be deterministic”
- Nested scope: “Phase X MAY be nondeterministic”

Invalid. MUST hard-fail.

---

## 19.6 Directory-Specific Examples (Normative)

### 19.6.1 `schemas/AGENTS.md`
May include:
- stricter schema linting rules
- naming conventions
- overlay declaration requirements

Must not:
- allow destructive schema edits
- relax validation coverage
- bypass overlay evolution rules

---

### 19.6.2 `generator/AGENTS.md`
May include:
- execution tooling requirements
- performance or cost budgets
- recursion depth caps tighter than root

Must not:
- change canonical phase order
- introduce nondeterminism into required phases
- bypass audit logging

---

### 19.6.3 `docs/AGENTS.md`
May include:
- formatting rules
- terminology enforcement checks
- citation requirements

Must not:
- introduce operational instructions
- redefine glossary terms
- contradict repository terminology

---

## 19.7 Inline Scope Directives (File-Level)

Inline scope directives MAY be used **only** to further restrict behavior.

They MUST:
- be explicit
- be local to the file
- reference the governing scope

Example:
`yaml`
# scope: schemas
# additional_constraints:
#   - no_backward_incompatible_changes

Inline directives MUST NOT:

relax parent or root constraints

override invariants

change enforcement behavior



---

19.8 Conflict Resolution Rule (Fail-Closed)

If two scopes provide conflicting instructions:

1. Apply the higher-precedence scope


2. Apply the more restrictive rule


3. If ambiguity remains, fail closed



Agents MUST NOT guess intent or attempt to reconcile ambiguity informally.


---

19.9 Required Agent Behavior on Scope Detection

When operating in any directory, agents MUST:

1. Identify the nearest AGENTS.md


2. Traverse upward to the root AGENTS.md


3. Compute the effective scope as the intersection of all applicable scopes


4. Apply the most restrictive interpretation



Failure to detect or apply a nested scope is a compliance violation.


---

19.10 Scope Auditability Requirement

Nested scopes MUST be auditable.

Each nested AGENTS.md SHOULD include:

scope name

parent scope reference

rationale for additional constraints


Changes to nested scopes MUST:

be reviewed as policy changes

produce an evidence bundle

not be bundled silently with unrelated changes



---

19.11 Explicit Non-Scopes

The following do not create scopes:

comments without normative language

README files

code comments

commit messages

CI configuration alone


Only an explicit AGENTS.md file defines a scope.


---

19.12 Enforcement Summary

Nested scopes exist to tighten, not loosen, controls

Invariants propagate downward

Constraints may only narrow

Ambiguity fails closed

Root scope authority is absolute

---



End of AGENTS.md.
