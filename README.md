# **sswg–MVM v.0.0.9mvm**  
### *sswg — Synthetic Synthesist of Workflow Generation (Minimum Viable Model)*

<div id="top"></div>
<div align="center">
   <img src="raven.svg" width="180" alt="Raven Recordings Logo">
</div>

<div align="center">
<h2>sswg–MVM</h2>
<i>Recursive, Schema-Aligned Workflow Engine • Designed by Tommy Raven</i>
</div>

<div align="center">

![Status](https://img.shields.io/badge/Status-Active-7E3ACE?style=for-the-badge)
![Build](https://img.shields.io/badge/Build-Stable-4B9CD3?style=for-the-badge)
![Version](https://img.shields.io/badge/v.09.mvm.25-Pre--Release-9E3CE7?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Architecture](https://img.shields.io/badge/Architecture-Recursive_AI-black?style=for-the-badge)
![License](https://img.shields.io/badge/License-Proprietary_(Pre--Release)-black?style=for-the-badge)

</div>

> **Pre-release notice:** sswg–MVM is proprietary software; private evaluation is allowed, but redistribution, hosting, model-training, or derivative use is prohibited.

---

## ⚖️ Legal At-A-Glance

**Current Status (v0.0.9mvm)**  
- Proprietary • All rights reserved  
- No redistribution, resale, hosting, or dataset extraction  
- No forks or derivative systems  
- Local evaluation permitted only  

**Future Licensing (v1.0.0ts)**  
- Licensed Use Only  
- No ownership transfer  
- No commercial redistribution  
- No agent/model training  

See: `LICENSE.md` and `TERMS_OF_USE.md`.

---

## 🧠 Overview

**sswg–MVM** is the Minimum Viable Model of *sswg — Synthetic Synthesist of Workflow Generation*:  
a recursive, schema-aligned AI engine that creates deterministic, multi-phase instructional workflows.

Instead of producing isolated responses, **sswg** synthesizes structured systems:

- Multi-phase workflow specifications  
- Dependency graphs (DAG-based)  
- Schema-validated JSON artifacts  
- Versioned lineage records  
- Recursive refinement cycles  

Author: **Tommy Raven (Thomas Byers)**  
© Raven Recordings ©️ 2025  

---

## 🧩 System Design Philosophy

**“Teach the workflow how to teach itself.”**

### Recursion  
Workflows become seeds for subsequent generations.

### Schema Integrity  
Strict JSON schema validation guarantees reproducibility.

### Modularity  
Phases → tasks → dependencies → evaluation → refinement.

### Determinism  
Outputs are stable, regenerable, and lineage-tracked.

---

## 🏛 System Architecture

    SSWG-mvm1.0/
    ├── generator/
    │     └── main.py                 → Primary workflow generator entry point
    ├── ai_validation/                → JSON schema enforcement
    ├── ai_graph/                     → DAG building & correction logic
    ├── ai_recursive/                 → Recursion engine
    ├── ai_memory/                    → Lineage & version tracking
    ├── ai_visualization/             → Mermaid & Graphviz exporters
    ├── ai_monitoring/                → Logging & telemetry
    ├── data/templates/               → Seed workflow templates
    └── schemas/                      → Canonical JSON schemas

- **System Overview:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Agent Roles & Handoffs:** [docs/AGENT_ROLES.md](docs/AGENT_ROLES.md)

---

## ⭐ Core Features

- Template-driven workflow synthesis  
- Recursive refinement engine  
- Strict schema validation (Draft 2020-12)  
- Dependency graph construction & autocorrection  
- JSON + Markdown artifact exporters
- Mermaid diagram generation
- Version history + lineage tracking
- CI/CD workflow automation (tests, PRs, docs)
- Role-separated agents with documented creator/critic/curator hand-offs

---

## 🌀 Operational Pipeline

1. Load template  
2. Normalize input and validate against schema  
3. Build dependency graph (DAG)  
4. Execute recursive refinement steps  
5. Produce artifacts (JSON, Mermaid, Markdown)
6. Record lineage snapshot
7. Auto-bump version if core modules changed

### Reproducible demo

Run the complete recursive pipeline (validation → evaluation → recursion → exports)
from the repo root with a single command:

```bash
python generator/main.py --demo --preview
```

Outputs land in `data/outputs/demo_run` and include:
- Refined workflow JSON + Markdown
- Mermaid + Graphviz diagrams
- Before/after metric plot (`metrics_before_after.svg`)
- Evaluation deltas and history snapshots

---

## 📄 Included Templates

| Template File                       | Domain         | Purpose                                |
|------------------------------------|----------------|----------------------------------------|
| `creative_writing_template.json`   | Literary Arts  | Narrative & poetic workflow structures |
| `technical_procedure_template.json`| Engineering    | SOP-style procedural workflows         |
| `meta_reflection_template.json`    | Metacognition  | Self-evaluating process frameworks     |
| `training_curriculum_template.json`| Education      | Modular curriculum design structures   |

---

## 🛠 Setup & Usage

### Clone the Repository

    git clone https://github.com/Tommy-Raven/SSWG-mvm1.0.git
    cd SSWG-mvm1.0

### Install Dependencies

    pip install -r requirements.txt

### Run the Generator (exact entry path)

    python3 generator/main.py --template creative --preview

Artifacts will be created under:

    data/outputs/


## 🧪 Testing

Run the full test suite:

    pytest -v

Test coverage includes:

- CLI behaviors  
- Template normalization  
- Schema validation  
- Graph engine  
- Recursive engine  
- Exporters  
- Version diffing  
- End-to-end workflow lifecycle  


## 🔄 CI/CD Automation

### Implemented

- Auto-version bump  
- Automated documentation generation  
- Full test execution  
- Auto-PR generation for version bumps  

### Planned  

- MkDocs documentation site on GitHub Pages  

---

## 👤 Author & Contact

**Tommy Raven**  
AI Researcher • Workflow Engineer • Python Developer  
© Raven Recordings, LLC 2025  

GitHub: **https://github.com/Tommy-Raven/SSWG-mvm1.0**  
Pronouns: *Apache / Helicopter*  
Fun fact: *Not actually an Apache helicopter — but thriving anyway.*  

---

## 📜 License Summary

**sswg–MVM is proprietary pre-release software.**  
Private evaluation is permitted; redistribution, resale, hosting, model-training,  
or derivative works are **not allowed**. See full terms in `LICENSE.md`.

---

<div align="center">
<a href="#top">
<img src="assets/footer.png" width="100%" alt="Raven Recordings Footer" aria-hidden="true">
</a>
</div>

---

## 🧩 Version Scheme Legend

- **vXX.xx.yy[tag][+tag]**  
  - **XX** = major system architecture revision
  - **xx** = minor system architecture revision  
  - **+tag** = specific os/development series. *Model Versions appended first, no '+' symbol, OS versioning is non-hierarchal, and appended with an '+' symbol, i.e., > minimum viable model: 'mvm', Debian: '+deb', ChromeOS: '+cros', Transitive Semantic Version: 'ts', Deterministic Version: 'dtr', etc*
  - **yy** = iterative refinement/patch release  
- **Pre-release** (like `v0.0.9mvm`) = additional licensing restrictions apply.
