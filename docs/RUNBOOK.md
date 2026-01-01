# Deterministic Runbook (sswg/mvm)

**Canonical status (primary entrypoint for how to run + expected outputs):** This runbook is the single canonical guide for deterministic, audit-ready runs of the sswg/mvm pipeline. Other docs are secondary/overview and should defer here to avoid drift.

## Deterministic Run Recipe

### 1) Validate the PDL phase set (required)

**Command**
```bash
python3 -m generator.pdl_validator pdl/example_full_9_phase.yaml schemas
```

**Inputs**
- `pdl/example_full_9_phase.yaml` (full_9_phase declaration)
- `schemas/` (PDL wrapper + phase schemas)

**Expected result**
- Validation completes without errors. No artifacts are written; the command prints validation output to stdout/stderr.

**Handler resolution**
- Canonical handlers live in `pdl/handlers.py` and are referenced as `pdl.handlers.<phase>`.
- Validation fails fast if any handler is missing or not callable.

---

### 2) Run a deterministic workflow execution

**Command**
```bash
python3 generator/main.py --demo --no-refine
```

**Inputs**
- `data/templates/campfire_workflow.json` (seed workflow used by `--demo`)
- `schemas/` (workflow schema validation)

**Expected artifacts (paths, filenames, contents)**
- `data/outputs/demo_run/workflow_<workflow_id>_<timestamp>.json`
  - Workflow payload (phases, modules, evaluation summaries, dependency graph metadata).
- `data/outputs/demo_run/workflow_<workflow_id>_<timestamp>.md`
  - Human-readable phase/task summary with evaluation notes.
- `data/outputs/demo_run/workflow_graph_<timestamp>.dot`
  - Graphviz DOT file capturing dependency nodes and edges.

> Determinism note: `--no-refine` disables the recursive refinement step to keep the run deterministic.

---

### 3) (Optional) Run the PDL runtime demo

**Command**
```bash
python3 generator/main.py --pdl pdl/default-pdf.yaml --demo
```

**Inputs**
- `pdl/default-pdf.yaml` (PDL demo configuration)
- `schemas/` (PDL schema validation)

**Expected artifacts**
- `data/outputs/demo_run/pdl_runs/pdl_run_<inputs_hash>.json`
  - PDL runtime report containing phase status, inputs hash, and artifact references.

---

## Expected Outputs Checklist (drift-free patterns)

### Deterministic workflow run
- [ ] `data/outputs/demo_run/workflow_<workflow_id>_<timestamp>.json`
- [ ] `data/outputs/demo_run/workflow_<workflow_id>_<timestamp>.md`
- [ ] `data/outputs/demo_run/workflow_graph_<timestamp>.dot`

### Optional PDL runtime run
- [ ] `data/outputs/demo_run/pdl_runs/pdl_run_<inputs_hash>.json`
