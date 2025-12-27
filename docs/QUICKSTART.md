# Quickstart Guide â€” SSWG-MVM

Welcome to **SSWG-MVM (Synthetic Synthesist of Workflow Generation â€” Minimum Viable Model)**.

This system generates, evaluates, and recursively evolves instructional workflows, producing both **human-readable** and **machine-readable** outputs. It is designed for reproducibility, extensibility, and research-grade inspection.

This Quickstart is intentionally minimal: it gets you from clone â†’ first run â†’ understanding recursion.

---

## ðŸš€ Getting Started

### 1. Clone the Canonical Repository

```bash
git clone https://github.com/Tommy-Raven/SSWG-mvm1.0.git
cd SSWG-mvm1.0
```

### 2. Install Dependencies

Using pip:

```bash
pip install -r REQUIREMENTS.txt
```

For fully reproducible environments, see:
- `reproducibility/`
- `docker/Dockerfile`

---

### 3. Run the Main Generator

```bash
python generator/main.py
```

This executes the default MVM pipeline:
- schema validation
- dependency resolution
- workflow generation
- evaluation and scoring
- export of artifacts

---

### 4. Trigger Recursive Refinement (Optional)

When prompted during execution, choose the option to **refine or expand** the workflow.

Recursive execution will:
- generate variant workflows,
- evaluate semantic and quality deltas,
- select or merge improved results,
- record metrics and lineage.

---

## ðŸ›  Requirements

- Python 3.11+
- Git
- Optional but recommended:
  - Docker (containerized execution)
  - VS Code or compatible editor

---

## ðŸ“‚ Outputs

The system produces:

- Human-readable artifacts:
  - Markdown (`.md`)
- Machine-readable artifacts:
  - JSON (`.json`)

All generated outputs, diagrams, metrics, and history snapshots are written to:

```
data/outputs/
```

Artifacts are additive-only and versioned for traceability.

---

## ðŸ— Architecture Reference

For a complete, code-aligned system description, see:

```
docs/ARCHITECTURE.md
```

This document defines:
- subsystem responsibilities,
- recursion and feedback loops,
- evaluation metrics,
- demo pipeline structure,
- and governance invariants.

Canonical invariants (including schema validation invariants) are defined in [invariants.yaml](../invariants.yaml) and detailed in [root_contract.yaml](../root_contract.yaml).

---

## ðŸ”§ Core Directories (At a Glance)

| Directory | Purpose |
|--------|--------|
| generator/ | Workflow execution, recursion, export, history |
| ai_core/ | Orchestration, phase control, lifecycle |
| ai_recursive/ | Variant generation, merging, version control |
| ai_evaluation/ | Semantic and quality scoring |
| ai_memory/ | Persistence, benchmarks, feedback |
| ai_graph/ | Dependency and semantic graph logic |
| ai_validation/ | Schema governance and regression safety |
| ai_visualization/ | Diagram and artifact rendering |
| schemas/ | Canonical contracts |
| artifacts/ | Generated outputs |
| docs/ | Documentation and guides |

---

## ðŸ”„ Conceptual Workflow Phases

The MVM pipeline follows these high-level phases:

1. Initialization and input acquisition  
2. Structural validation against schemas  
3. Workflow generation and modular expansion  
4. Evaluation and semantic scoring  
5. Recursive refinement and evolution  
6. Visualization and artifact export  
7. Memory persistence and feedback logging  

Exact execution order and responsibilities are defined in `docs/ARCHITECTURE.md`.

---

## âš¡ Tips

- Use `generator/main.py` for local CLI execution.
- Recursive runs improve clarity and reduce redundancy over iterations.
- All outputs are versioned; inspect diffs to understand evolution.
- Metrics and feedback guide recursion decisions.

---

This Quickstart provides everything needed to generate your first workflow, inspect its evaluation, and optionally explore recursive self-improvement.
