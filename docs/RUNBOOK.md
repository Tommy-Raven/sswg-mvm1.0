# Deterministic Run Recipe (sswg/mvm)

This runbook is the single canonical guide for deterministic, audit-ready runs of the sswg/mvm pipeline.

## Deterministic Run Recipe

### 1) Validate the PDL phase set

**Command**
```bash
python -m generator.pdl_validator pdl/example_full_9_phase.yaml schemas
```

**Inputs**
- `pdl/example_full_9_phase.yaml` (full_9_phase declaration)
- `schemas/` (PDL wrapper + phase schemas)

**Expected result**
- Validation completes without errors. No artifacts are written; the command prints validation output to stdout/stderr.

---

### 2) Run a deterministic workflow execution

**Command**
```bash
python generator/main.py \
  --workflow-json data/templates/campfire_workflow.json \
  --no-refine \
  --out-dir data/outputs
```

**Inputs**
- `data/templates/campfire_workflow.json` (seed workflow)
- `schemas/` (workflow schema validation)

**Expected artifacts (paths, filenames, contents)**
- `data/outputs/<workflow_id>.json`
  - Full workflow payload (phases, modules, evaluation summaries, dependency graph metadata).
- `data/outputs/<workflow_id>.md`
  - Human-readable phase/task summary with evaluation notes.
- `data/outputs/workflow_<workflow_id>_<timestamp>.json`
  - Timestamped visualization JSON export of the workflow payload.
- `data/outputs/workflow_<workflow_id>_<timestamp>.md`
  - Timestamped visualization Markdown export (phase overview and metadata).
- `data/outputs/workflow_graph_<timestamp>.dot`
  - Graphviz DOT file capturing dependency nodes and edges.

> Determinism note: `--no-refine` disables the recursive refinement step to keep the run deterministic.

---

## Expected Outputs Checklist

### data/outputs/ (repository snapshots)
- [ ] `data/outputs/meta_template_20251203230038.md`
- [ ] `data/outputs/training_template_20251207034010.md`
- [ ] `data/outputs/training_template_20251207034925.md`
- [ ] `data/outputs/unnamed_workflow.md`
- [ ] `data/outputs/workflow_001.md`

### Benchmark / profiling artifacts
- [ ] `artifacts/performance/benchmarks_20251227_090721.json` (benchmark results)
- [ ] `data/profiling/workflow_profiling_2025-12-27.json` (profiling summary)
- [ ] `data/profiling/campfire_workflow/` (profiling run directory)
- [ ] `data/profiling/technical_procedure_template/` (profiling run directory)
