---
anchor:
  anchor_id: api_generator
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# ⚙ Generator Module (generator/)  
### Core Pipeline for Workflow Transformation

The `generator` module provides the **primary MVM pipeline**:

- Template ingestion  
- Schema validation  
- DAG construction  
- Refinement (recursive-lite)  
- Evaluation  
- Artifact export (JSON + Markdown)  
- History tracking  

---

# 🧠 Key Entry Points

## `main.py`

### `run_mvm(workflow_path, out_dir, enable_refinement=True, enable_history=True, preview=False)`
Runs the full workflow transformation process.

**Returns**  
A refined, schema-aligned workflow dict.

### `process_workflow(workflow, enable_refinement=True)`
Core logic: validation → DAG → mermaid → refinement.

### `export_artifacts(workflow, out_dir)`
Writes JSON + Markdown artifacts.

### `record_history_if_needed(original, refined)`
Tracks lineage transitions when structure or score changes.

---

# 🔁 Refinement API

## `recursion_manager.simple_refiner(workflow)`
A single-iteration refinement pass:
- Adds missing fields  
- Strengthens logic statements  
- Performs safety normalizations  
- Prepares for recursive full-cycle (future)  

---

# 🔧 Exporters

## `export_json(workflow, out_dir)`
Writes minified canonical JSON.

## `export_markdown(workflow, out_dir)`
Human-readable Markdown export.

---

# 📂 Other components

- `async_executor.py` — future async benchmark runner  
- `cache_manager.py` — WIP persistence control  
- `evaluation.py` — bridges generator ↔ evaluation subsystem  
- `history.py` — workflow lineage manager
