> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

---
anchor:
  anchor_id: docs_index
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# 🐦 SSWG-MVM — Synthetic Synthesist of Workflow Generation  
### *Minimum Viable Model Documentation*  
Created by **Tommy Raven / Raven Recordings, LLC ©2025**

---

<div align="center">
<img src="assets/raven.svg" width="200px" alt="SSWG-MVM Logo"/>
</div>

<p align="center">
<a href="https://github.com/Tommy-Raven/sswg-mvm1.0">
<img src="https://img.shields.io/badge/SSWG-MVM-v1.2.0-purple?style=flat-square">
</a>
<img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square">
<img src="https://img.shields.io/badge/Status-Stable-green?style=flat-square">
<img src="https://img.shields.io/badge/License-Proprietary-lightgray?style=flat-square">
</p>

---

# 🌑 Overview

**SSWG-MVM** is a recursive, schema-aligned, instruction-generating AI engine capable of:

- interpreting high-level human goals  
- generating structured, multi-phase workflows  
- validating them with a strict JSON schema  
- evaluating clarity, coverage, and coherence  
- recursively refining outputs  
- exporting multi-format artifacts (JSON / Markdown / DAG)  
- preserving lineage through a version-aware memory system  

It is both **educator and apprentice** — each workflow seeds the next generation.

**Stability posture:** v1.2.0 is the current stable release for the MVM line, with canonical documentation and runbooks aligned to the 9-phase pipeline.

---

# 🧠 Core Capabilities

### ✔ Schema-driven workflow generation  
Ensures all workflows follow a canonical structure, metadata model, and dependency graph rules.

### ✔ Recursive refinement  
A minimal version of the recursion engine (MVM) enhances structure through a deterministic refinement pass.

### ✔ Built-in evaluation  
Clarity metrics, semantic checks, and dependency validation.

### ✔ Export & Visualization  
- Human-readable Markdown  
- Machine-ready JSON  
- Mermaid DAG diagrams  
- Future: Graphviz DOT, HTML, PDF

### ✔ Memory & Versioning  
- lineage tracking  
- diff-based regeneration triggers  
- auto version bump via CI/CD

---

# 🧩 Project Structure

```
sswg-mvm1.0/
│
├── ai_conductor/              # Orchestration, workflow assembly
├── ai_recursive/         # Diff engine, variant synthesis
├── ai_memory/            # Persistent logs, feedback integrator
├── ai_evaluation/        # Metrics, semantic scoring
├── ai_validation/        # Schema validator
├── ai_graph/             # DAG construction
├── ai_visualization/     # Mermaid / export tools
├── generator/            # Main MVM engine
├── data/templates/       # Editable starter workflows
├── docs/                 # MkDocs site (this)
└── tests/                # Pytest suite
```

---

# 🚀 Quickstart

### Install dependencies
```bash
pip install -r requirements.txt
```

### Generate your first workflow
```bash
python3 -m generator.main --preview
```

### Use a template
```bash
python3 -m generator.main --template creative
```

### Export artifacts
Outputs appear under:
```
data/outputs/
```

---

# 📚 Documentation Map

| Section | Description |
|--------|-------------|
| **Getting Started** | Install, run MVM, understand workflow structure |
| **Architecture** | Full system map, recursion model, folder layout |
| **Templates** | All workflow templates with examples |
| **Schemas** | The JSON Schema that defines valid workflows |
| **Developer Docs** | CLI, modules, CI/CD, versioning |
| **Visualization** | Mermaid & DAG explanations |
| **Changelog** | Auto-generated version bumps |
| **Evolution Bundle** | Milestone lineage through v1.2.0 |
| **Version Lineage** | Build lineage from v0.1.0 through v1.2.0 |

---

# 🐦 About the Author

**Tommy Raven**  
AI Developer • Musician • Workflow Engineer  
Creator of **Raven Recordings, LLC**

---

<p align="center">Made with ⚡, recursion, and a slightly concerning amount of hyperfocus.</p>
