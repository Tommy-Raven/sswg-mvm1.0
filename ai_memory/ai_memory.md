# ai_memory — Memory, Feedback, and Benchmarks (SSWG MVM)

The `ai_memory` package is responsible for *state that persists across runs*:

- Workflow snapshots
- Evaluation + diff feedback
- Long-term performance benchmarks
- Basic anomaly detection on metrics

At the MVM stage, the emphasis is on **simple, inspectable storage**, not
on heavy databases or distributed systems.

---

## Components

### 1. `memory_store.py` (existing)

**Role:** Canonical storage for workflow-like objects.

Typical responsibilities:

- `save(obj)` — store a workflow / artifact snapshot.
- `load_latest(key)` — retrieve latest snapshot for a given id (optional).
- Possibly maintain a simple on-disk JSONL or directory of files.

This module is already in use by:

- `ai_core.orchestrator.Orchestrator` (saving final workflows)
- `ai_recursive.memory_adapter.RecursiveMemoryAdapter` (saving variants)

---

### 2. `feedback_integrator.py` (existing)

**Role:** Aggregate feedback over recursive/evaluation cycles.

Responsibilities (as used elsewhere):

- `record_cycle(diff_summary, eval_metrics, regenerated: bool)`:
  - logs comparison between old/new workflows
  - stores evaluation metrics (e.g., clarity scores)
  - flags whether a regeneration was performed

It serves as a bridge between:

- diffs from `ai_recursive.version_diff_engine`
- metrics from `ai_evaluation`
- memory from `memory_store.py`

---

### 3. `anomaly_detector.py`

**Role:** Detect suspicious behavior in numeric metrics.

Examples:

- Latency spikes
- Error-rate anomalies
- Sudden drops in evaluation scores

MVM behavior:

- Fit simple mean/std baselines.
- Provide an `is_anomalous(value)` check.
- Provide a `score(value)` to express how far from baseline a metric is.

---

### 4. `benchmark_tracker.py`

**Role:** Track benchmarks over time.

Responsibilities:

- Record named benchmarks (e.g., `"campfire_workflow_quality"`).
- Track best scores and metadata (timestamp, version, workflow_id).
- Provide a `to_dict()` view for export / inspection.

This gives the system a crude “high score table” for different workflows
or model configurations.

---

## MVM Philosophy for Memory

- **Plain and transparent:** structures should be easy to read manually.
- **Composable:** each component can be used independently.
- **Upgradeable:** swapping in a DB or vector store later should not
  require rewriting the entire codebase.
