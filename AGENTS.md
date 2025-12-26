# AGENTS.md — sswg / mvm Compliance Operations Manual (v0.0.9mvm)

This document defines **mandatory** behaviors for all contributors, automation agents, CI runners, and tooling that touch this repository. Language is intentionally normative (**MUST / SHALL / SHOULD**) to function as an enforceable production standard.

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

## 1) Naming Discipline (Required)

- **sswg / mvm / nvm** refer to software components / behaviors (lowercase).
- **SSWG / MVM / NVM** refer to governance mindsets / mental models (uppercase).

Any documentation, logs, schemas, or code that violates this naming discipline **SHOULD** be corrected during the same change set.

---

## 2) Canonical Mission (Non-Negotiable)

### 2.1 sswg mandate
sswg **MUST** enforce a **phase-driven**, **audit-ready**, **9-phase** pipeline that yields deterministic measurement outputs where required.

### 2.2 mvm mandate
mvm defines the **minimum acceptable completeness** for sswg software. Workflows and tooling are invalid unless the full **9-phase** pipeline is supported and enforced.

---

## 3) Canonical 9-Phase Pipeline (Full Set, Ordered, Separated)

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

### 3.1 Phase separation
- Each phase **MUST** be declared explicitly and validated against its phase-specific schema.
- Phase behaviors **MUST NOT** be collapsed, merged, skipped, or reordered.
- Any attempt to combine phase responsibilities **MUST** hard-fail (see Failure Labeling).

### 3.2 Determinism requirements
Determinism is **required** for phases:
- `normalize`
- `analyze`
- `validate`
- `compare`

Interpretation is explicitly **nondeterministic** and **MUST** be labeled as such (see §8.4).

---

## 4) Global Canon Requirements (Apply to All Work)

### 4.1 Canonic anchoring (required metadata)
Every artifact produced or modified in this repo **MUST** have a canonical anchor containing:

- `anchor_id`
- `anchor_version`
- `scope`
- `owner`
- `status` ∈ {`draft`, `sandbox`, `canonical`, `archived`}

If an artifact format cannot embed this metadata inline, the metadata **MUST** exist as a colocated sidecar file or registry entry under an agreed canonical index.

### 4.2 Immutability of canon
- Once `status: canonical`, the anchored artifact **MUST** be immutable.
- Canonical changes **MUST** occur via delta overlays only (see §4.3).
- Any direct modification to a canonical anchor **MUST** hard-fail.

### 4.3 Cross-schema delta overlays (mandatory evolution mechanism)
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

## 5) Canonical Schema Contracts (PDL)

### 5.1 Required schemas
The canonical PDL enforcement is:

- `schemas/pdl.json` (wrapper)
  - delegates to `schemas/pdl-phase-set.json`
  - which enforces the 9-phase ordered prefixItems set
- `schemas/pdl-phase-set.json`
- `schemas/pdl-phases/_common.json`
- `schemas/pdl-phases/{ingest,normalize,parse,analyze,generate,validate,compare,interpret,log}.json`

### 5.2 PDL validity requirement
- Any PDL document claiming `pipeline_profile: full_9_phase` **MUST** validate against `schemas/pdl.json`.
- A PDL document **MUST** contain exactly 9 phases in correct order (`prefixItems` enforcement).
- `items: false` is authoritative: additional phases or reordering **MUST** fail validation.

### 5.3 Handler + IO requirements (PDL contract)
- Each phase **MUST** include:
  - `name`, `type`, `enabled`, `description`, `inputs`, `outputs`, `handler`
- Each `inputs[]` / `outputs[]` entry **MUST** conform to `_common.json#/$defs/io_item`.
- `id` fields **MUST** match: `^[a-z][a-z0-9_\-]*$`
- Phase schema constraints are authoritative. If a phase schema requires a constraint field, it **MUST** be present and correct.

### 5.4 Phase-specific constraint invariants (enforced by schema)
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

## 6) Repository Layer Policy (Immutable vs Additive)

### 6.1 Canonical layers (immutable)
The following directories are canonical layers and **MUST** be treated as immutable in production:

- `generator/`
- `cli/`
- `pdl/`
- `reproducibility/`

Changes to these layers **SHOULD** be minimized and **MUST** pass all required validation gates before promotion.

### 6.2 Generated layers (additive-only)
The following directories are generated layers and **MUST** be additive-only:

- `artifacts/`
- `data/`
- `docs/`

No destructive edits (delete/overwrite) are permitted in these layers unless a formally approved archival policy exists and is invoked explicitly.

---

## 7) Validation Gates (Promotion Blocking, Required)

Promotion, merge, release, or “canonical” marking **MUST** be blocked unless all required gates pass:

1. `schema_validation`
2. `phase_schema_validation`
3. `invariants_validation`
4. `reproducibility_validation`

A gate failure **MUST**:
- emit the correct failure label, and
- stop execution.

---

## 8) Failure Labeling Standard (Hard-Fail, Typed, Auditable)

### 8.1 Required failure label fields
On any failure, the failing phase **MUST** emit a failure label containing:

- `Type`
- `message`
- `phase_id`

### 8.2 Allowed failure types
`Type` **MUST** be one of:
- `deterministic_failure`
- `schema_failure`
- `io_failure`
- `tool_mismatch`
- `reproducibility_failure`

### 8.3 Hard-fail policy
- When any required invariant fails, the phase **MUST** emit a failure label and **MUST** hard-fail execution immediately.
- “Soft failures,” “warnings-only,” or “continue on error” behavior **MUST NOT** occur for required invariants.

### 8.4 Interpret phase labeling (nondeterministic)
- `interpret` outputs **MUST** be labeled nondeterministic and **MUST** reference measured artifacts only.
- `interpret` **MUST NOT** mutate measurement outputs or canonical anchors.

---

## 9) Validator Operations (Required Tooling + Exact Actions)

### 9.1 Required validator entrypoint
The repo **MUST** provide a validator module capable of:

- loading `schemas/pdl.json` (wrapper → phase set),
- resolving local `$ref` across `schemas/pdl-phases/*`,
- validating PDL YAML/JSON,
- emitting correctly typed failure labels,
- exiting non-zero on failure.

### 9.2 Phase ownership of schema validation failures
Schema validation failures **MUST** be labeled:
- `Type: schema_failure`
- `phase_id: validate`

### 9.3 Required pre-run action
Agents and CI **MUST** validate any PDL before execution.

✅ `python -m generator.pdl_validator pdl/example_full_9_phase.yaml schemas`

If the repo uses a different invocation, it **MUST** be documented and behaviorally equivalent.

---

## 10) Compare Phase Requirements (Deterministic Deltas)

- `compare` **MUST** be deterministic.
- If overlap metrics are used, they **MUST** be restricted to:
  - `iou`
  - `jaccard`
- Compare outputs **MUST** be replayable and suitable for audit trails.

---

## 11) Log Phase Requirements (Audit-Ready Output)

The `log` phase **MUST** emit audit-ready outputs including:
- `run_id`
- input hashes (`inputs_hash_required`)
- per-phase status (`phase_status_required`)
- references to:
  - PDL used
  - schema versions
  - overlay versions
  - failure labels (if any)

Log outputs **MUST** be sufficient to replay deterministic phases and reconstruct causal lineage.

---

## 12) Agent Responsibilities (Exact Actions for Compliance)

All agents (human or automated) working in this repo **MUST** follow this sequence whenever they create/modify pipeline artifacts.

### 12.1 Before making changes
1. **MUST** identify affected phases (subset of the 9 canonical phases).
2. **MUST** identify touched layers:
   - canonical layers (immutable), or
   - generated layers (additive-only), or
   - schemas/pdl enforcement
3. **MUST** determine whether the change is:
   - overlay (default, permitted), or
   - base schema rewrite (disallowed unless explicitly authorized)

### 12.2 While making changes
1. **MUST** preserve phase separation and required constraints.
2. **MUST** preserve determinism requirements for required phases.
3. **MUST** ensure all updated artifacts carry canonical anchor metadata.
4. **MUST** ensure failures are labeled and hard-fail on invariant violation.

### 12.3 After making changes (required checks)
1. **MUST** validate all PDL documents against `schemas/pdl.json`.
2. **MUST** ensure per-phase schemas still validate.
3. **MUST** ensure validation gates pass before promotion.
4. **MUST** ensure log outputs contain run id + input hashes + statuses.
5. **MUST** provide reproducibility notes sufficient to replay deterministic phases.

If any check fails, the agent **MUST** stop and emit the correct typed failure label.

---

## 13) Prohibited Behaviors (Hard Stops)

The following are prohibited and **MUST** be treated as hard failures:

- Reordering, adding, or removing phases from `full_9_phase`.
- Collapsing phase behavior (e.g., parse+analyze).
- Introducing nondeterminism into `normalize`, `analyze`, `validate`, or `compare`.
- Using generative tooling to generate measurement keys (`no_generative_tools_for_measurement`).
- Directly mutating canonical anchors.
- Destructive edits in additive-only layers without explicit archival policy.
- Emitting untyped failures or failing silently.
- Violating root-scope agent rules (§0), including prohibited search commands and PR/commit flow.

---

## 14) Minimal Acceptance Criteria (Release/Promotion Readiness)

A change set is not promotion-ready unless:

- PDL validation passes (`schemas/pdl.json` wrapper).
- Phase schemas pass for all 9 phases.
- Determinism checks pass for required phases.
- Compare outputs are deterministic and metric-compliant.
- Interpret outputs are measured-only and labeled nondeterministic.
- Log outputs include run id, input hashes, statuses, and references.
- Failure labeling is correct under intentional violation tests.

---

## 15) Enforcement Policy (Authority)

- `sswg.yaml` has highest precedence; violation policy is `hard_fail`.
- `mvm.yaml` defines minimum acceptable completeness; missing requirements invalidate workflows.

Agents **MUST** treat these as authoritative constraints. No bypasses are permitted.

---

## 16) Quick Reference: Required Files (Minimum Set)

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
- `Type: reproducibility_failure` (if the environment cannot be reconstructed), or
- `Type: io_failure` (if the file path is missing/unreadable),
with `phase_id: validate` when discovered during validation.

---

## 17) Change Management (Required Workflow)

- If a task explicitly permits edits:
  - Agents **MUST** commit changes.
  - Agents **MUST** invoke `make_pr` with appropriate title and body.
  - Agents **MUST NOT** leave committed changes without calling `make_pr`.
  - Agents **MUST NOT** call `make_pr` without commits.
- If QA-only:
  - Agents **MUST NOT** modify repo contents.
  - Findings **MUST** include `task-stub` blocks after each issue.

---

## 18) Reporting Format Requirements (When Providing Findings)

- Each issue description **MUST** be followed immediately by a `task-stub` block.
- Testing/check commands **MUST** be prefixed with emojis:
  - ✅ pass
  - ⚠️ warning/limitation
  - ❌ fail
- If TODOs/placeholders remain in the final diff:
  - Agents **MUST** include **Notes** after **Testing**.
  - Agents **MUST** omit **Notes** if none exist.

---

## 19) Required Example PDL Artifact

The repo **SHOULD** maintain:
- `pdl/example_full_9_phase.yaml` as a canonical example that validates against `schemas/pdl.json`.

If the example fails schema validation, agents **MUST** treat it as a gating defect and block promotion.

---

End of AGENTS.md.
