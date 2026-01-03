---
anchor:
  anchor_id: docs_visualization_guide
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# Visualization Guide — AI Instructions Workflow Generator

## Overview

This guide details the visualization pipeline for recursive workflow generation and evaluation. The system produces both live and static visual outputs, enabling users to trace workflow progression, recursive feedback, and module interactions.

---

## 🟧 Core Modules

* `workflow_engine.py` — Orchestrates all workflow phases and manages execution flow.
* `graph_engine.py` — Generates dependency and phase graphs (Mermaid / Graphviz).
* `recursion_manager.py` — Controls recursion depth and iterative workflow expansion.
* `evaluation_engine.py` — Calculates clarity, coverage, and translatability scores.
* `visualizer.py` — Renders diagrams for human inspection and reporting.
* `io_manager.py` — Handles Markdown, JSON, and Graphviz output generation.

---

## 🟦 Input / Output Interfaces

* User CLI input triggers workflow generation.
* Outputs include:

  * Markdown documentation (`.md`)
  * Machine-readable JSON (`.json`)
  * Graph visualization files (`.gv` / `.png`)

---

## Data Flow Diagram

flowchart LR
U[🟦 User Input / CLI]:::cli --> WF[🟧 workflow_engine.py]:::module
WF --> GE[🟧 graph_engine.py]:::module
GE --> RM[🟧 recursion_manager.py]:::module
RM --> EE[🟧 evaluation_engine.py]:::module
EE --> VF[🟧 visualizer.py]:::module
VF --> IO[🟧 io_manager.py]:::module
IO --> UO[🟦 User Output (Markdown / JSON / Graphviz)]:::cli

EE -. feedback .-> WF
RM -. recursion_control .-> WF

---

## Notes

* Evaluation and recursion feedback loops ensure that each workflow iteration refines and improves prior outputs.
* Visualization files are automatically updated with each recursive generation cycle.
* The guide supports both CLI and programmatic invocation for flexible deployment.

---

## 📈 Verity–Entropy Convergence Templates

Use these templates to visualize bounded cognition convergence in reports:

```mermaid
xychart-beta
  title "Verity vs Entropy"
  x-axis "Iteration" 1 2 3 4 5
  y-axis "Score" 0 0.25 0.5 0.75 1.0
  line "Verity" 0.45 0.58 0.67 0.72 0.74
  line "Entropy" 0.12 0.20 0.33 0.48 0.66
```

```mermaid
xychart-beta
  title "Verity Ratio"
  x-axis "Iteration" 1 2 3 4 5
  y-axis "Ratio" 0 1 2 3 4 5 6
  line "Determinism/Entropy" 3.8 3.1 2.7 2.1 1.7
```
