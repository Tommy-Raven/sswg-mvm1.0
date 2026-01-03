--- 

anchor:
  anchor_id: docs_runbook101
  anchor_version: "1.0.0+mvm"
  scope: docs
  owner: sswg-core
  status: canonical
  output_mode: non_operational_output

--- 


# Local Runtime Runbook 101 (sswg–mvm)

> **Purpose:**  
> This guide defines the canonical procedure for executing deterministic, local Python-based runs of the `sswg–mvm` (software) system.  
> It is intended for controlled local testing, validation, and audit-ready artifact generation under Python 3.

> **Scope:**  
> Local deterministic operation of the 9-phase workflow using direct `python3` invocation.  
> CLI automation and orchestration are outside this document’s scope.

---

## Canonical Definition

Local runs are treated as **bounded_recursion** sequences executed under explicit constraints and invariants.  
All outputs are **non_operational artifacts**—no real-world procedures or automation.

The reference configuration yields:

- Deterministic evaluation gates (no refinement)
- Fully validated schema compliance
- Immutable evidence_bundles stored under `/data/outputs/`

---

## Phase Integrity Model

Each local run traverses the canonical 9-phase model:

```

ingest → normalize → parse → analyze → generate → validate → compare → interpret → log

````

- Phases up to `compare` are deterministic.
- Phase `interpret` is explicitly **nondeterministic** under controlled variance.
- Phase `log` finalizes the evidence_bundle.

---

## 1. Validate Phase Definitions (PDL)

**Objective:** Confirm that all declared phases and handlers match schema definitions and repository constraints.

**Invocation:**
```bash
python3 -m generator.pdl_validator pdl/example_full_9_phase.yaml schemas
````

**Inputs:**

* `pdl/example_full_9_phase.yaml` — canonical phase declaration
* `schemas/` — phase schema directory

**Expected Artifact (stdout only):**
A validated phase report indicating pass/fail for each canonical phase.
No files are written; this process confirms structural integrity only.

**Validation Invariants:**

* All phases defined in schema: required
* All handler references resolvable: required
* No nondeterministic phase mislabeled as deterministic: required

---

## 2. Execute Deterministic Workflow

**Objective:** Produce a complete, audit-ready workflow artifact using fixed templates and schema constraints.

**Invocation:**

```bash
python3 generator/main.py --demo --no-refine
```

**Inputs:**

* `data/templates/campfire_workflow.json` — canonical seed template
* `schemas/workflow_schema.json` — schema validator

**Resulting Artifacts:**

* `data/outputs/demo_run/workflow_<workflow_id>_<timestamp>.json`
  Contains: phase lineage, dependency graph, module registry snapshot.
* `data/outputs/demo_run/workflow_<workflow_id>_<timestamp>.md`
  Contains: human-readable phase documentation (non_operational_output).
* `data/outputs/demo_run/workflow_graph_<timestamp>.dot`
  Contains: deterministic dependency graph for external audit tools.

**Constraint Flags:**

* `--no-refine` enforces bounded_recursion depth = 0 (deterministic)
* `--demo` substitutes internal test data for live context

**Validation Gates Triggered:**

* Schema conformity
* Invariant enforcement
* Consistency cross-checks

---

## 3. (Optional) Execute PDL Runtime Evaluation

**Objective:** Evaluate a PDL configuration through deterministic runtime inspection for constraint conformity.

**Invocation:**

```bash
python3 generator/main.py --pdl pdl/default-pdf.yaml --demo
```

**Inputs:**

* `pdl/default-pdf.yaml` — sample PDL configuration
* `schemas/` — schema set for PDL validation

**Resulting Artifact:**

* `data/outputs/demo_run/pdl_runs/pdl_run_<inputs_hash>.json`
  Contains: evidence_bundle including constraint states, inputs hash, and evaluation_gate status.

---

## 4. (Optional) Verify Artifacts and Hashes

**Objective:** Confirm that evidence_bundles and outputs match deterministic expectations.

**Invocation:**

```bash
python3 -m ai_validation.schema_validator data/outputs/demo_run/ schemas/workflow_schema.json
```

**Expected Output:**

* `stdout` summary indicating all bundles valid and unaltered.
* Hash manifest verification for each artifact in the bundle.

---

## Artifact Inventory

| Path                                                        | Artifact Type          | Determinism   | Description                     |
| ----------------------------------------------------------- | ---------------------- | ------------- | ------------------------------- |
| `data/outputs/demo_run/workflow_<id>_<timestamp>.json`      | evidence_bundle        | deterministic | Workflow output (canonical)     |
| `data/outputs/demo_run/workflow_<id>_<timestamp>.md`        | non_operational_output | deterministic | Human-readable workflow summary |
| `data/outputs/demo_run/workflow_graph_<timestamp>.dot`      | artifact               | deterministic | Dependency graph for inspection |
| `data/outputs/demo_run/pdl_runs/pdl_run_<inputs_hash>.json` | evidence_bundle        | deterministic | Optional PDL runtime validation |

---

## Drift-Free Validation Checklist

* [ ] PDL schema validated via `pdl_validator`
* [ ] Workflow artifacts generated deterministically (`--no-refine`)
* [ ] Evidence_bundle verified via schema validator
* [ ] No nondeterministic labeling errors
* [ ] All outputs classified as `non_operational_output`
* [ ] Anchor metadata blocks preserved

---

## Governance Metadata

```yaml
terminology_compliance: "TERMINOLOGY.md@1.3.0+mvm"
constraint_scope: "local_deterministic_runtime"
audit_surface: "data/outputs/demo_run/"
recursion_depth_limit: 0
nondeterministic_phase: interpret
fail_closed: true
```

---

### Summary

This document defines the **canonical, bounded_recursion local runtime model** for `sswg–mvm`.
All local runs must:

* Pass PDL and schema validation,
* Produce deterministic, audit-ready evidence_bundles,
* Emit non_operational_output only,
* Conform to phase determinism labeling as defined in `TERMINOLOGY.md`.

> **Status:** canonical reference for local deterministic operation
> **Next:** see `docs/runbook.md` for system-level CI and multi-node orchestration.

--- 

End of Document — runbook101.md (v1.0.0+mvm)

--- 
