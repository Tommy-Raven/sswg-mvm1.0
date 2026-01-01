---
anchor:
  anchor_id: readme
  anchor_version: "1.2.0"
  scope: documentation
  owner: sswg
  status: draft
---

# **sswg-mvm v1.2.0**  
### *sswg — Synthetic Synthesist of Workflow Generation (minimum viable model)*

<div id="top"></div>
<div align="center">
   <img src="raven.svg" width="180" alt="Raven Recordings Logo">
</div>

<div align="center">
<h2>sswg-mvm</h2>
<i>A schema-governed, entropy-aware recursive cognition engine • Designed by Tommy Raven</i>
</div>

<div align="center">

![Status](https://img.shields.io/badge/Status-Active-7E3ACE?style=for-the-badge)
![Build](https://img.shields.io/badge/Build-Stable-4B9CD3?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.2.0--Bounded%20Cognition-blue)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Architecture](https://img.shields.io/badge/Architecture-Recursive_AI-black?style=for-the-badge)
![License](https://img.shields.io/badge/License-Proprietary_(Pre--Release)-black?style=for-the-badge)

</div>

> **Pre-release notice:** sswg-mvm is proprietary software; private evaluation is allowed, but redistribution, hosting, model-training, or derivative use is prohibited.

---

## ⚖️ Legal At-A-Glance

**Current Status (v1.2.0)**  
- Proprietary • All rights reserved  
- No redistribution, resale, hosting, or dataset extraction  
- No forks or derivative systems  
- Local evaluation permitted only  

**Future Licensing (v1.0.0ts)**  
- Licensed use only  
- No ownership transfer  
- No commercial redistribution  
- No agent/model training  

See: `LICENSE.md` and `TERMS_OF_USE.md`.

---

## 🧠 Overview

**sswg-mvm** is the minimum viable model of *sswg — Synthetic Synthesist of Workflow Generation*:  
a recursive, schema-aligned AI engine that creates deterministic, multi-phase instructional workflows.

Instead of producing isolated responses, **sswg** synthesizes structured systems:

- Multi-phase workflow specifications (canonical 9-phase pipeline)
- Dependency graphs (DAG-based)
- Schema-validated JSON artifacts
- Versioned lineage records
- Recursive refinement cycles

Author: **Tommy Raven (Thomas Byers)**  
© Raven Recordings ©️ 2025  

---

## ✨ Key Features (v1.2.0)

- Bounded cognition via entropy control and termination guards.
- Verity tensor metric for semantic, deterministic, and entropic alignment.
- Ontology-aligned optimization subsystem for deterministic telemetry.

---

## ▶️ Canonical Runbook

**Primary entrypoint (how to run + expected outputs):**  
docs/RUNBOOK.md

Other docs are secondary/overview and should defer to the canonical runbook above.

---

## ⚡ Quick Start (Bounded Cognition)

```bash
python -m generator.recursion_manager --bounded
```

See [CHANGELOG.md](CHANGELOG.md) for the v1.2.0 release notes.

---

## 🧩 System Design Philosophy

**“Teach the workflow how to teach itself.”**

### Recursion  
Workflows become seeds for subsequent generations.

### Schema Integrity  
Strict JSON schema validation enforces invariants that support reproducibility. See the canonical definitions in [invariants.yaml](invariants.yaml) and [root_contract.yaml](root_contract.yaml).

### Modularity  
Phases → tasks → dependencies → evaluation → refinement.

### Determinism  
Outputs are stable, regenerable, and lineage-tracked. Determinism is required for `normalize`, `analyze`, `validate`, and `compare`.

---

## 📐 Formal Behavioral Semantics (Recursion, Metrics, Termination)

This section documents the concrete, implemented semantics used by the mvm
runtime for recursive refinement and evaluation. It is intended to be
machine-auditable and to mirror the behavior in `generator/recursion_manager.py`,
`ai_recursive/recursion_manager.py`, and `ai_evaluation/quality_metrics.py`.
The recursion policy described below is the authoritative behavior for
termination and guardrails; formal guarantees and assumptions are documented in
[docs/FORMAL_GUARANTEES.md](docs/FORMAL_GUARANTEES.md).

### Recursion Semantics (single-cycle refinement)
Each recursion cycle executes the following steps:

1. **Baseline evaluation:** `evaluate_workflow_quality` computes per-metric
   scores and an `overall_score` (average of metric values).
2. **Refinement proposal:** `generate_refinement` produces a candidate workflow
   and an LLM decision (e.g., `accept`, `revise`).
3. **Candidate evaluation:** the candidate is re-scored using the same metric
   set.
4. **Delta computation:**
   - `score_delta = candidate.overall_score - baseline.overall_score`
   - `semantic_delta = 1 - similarity(before, after)` where similarity is
     cosine similarity if sentence-transformers is available, otherwise a
     lexical set overlap proxy.
5. **Regeneration decision:** the candidate is adopted only if:
   - `llm_decision ∈ {"accept", "revise"}`, **and**
   - `depth < policy.max_depth`, **and**
   - (`score_delta ≥ policy.min_improvement` **or**
     `semantic_delta ≥ policy.min_semantic_delta`)
6. **State recording:** metric plots, diff summaries, feedback records, and
   lineage snapshots are persisted for auditability.

Default policy thresholds (subject to explicit override):
`max_depth = 2`, `min_improvement = 0.05`, `min_semantic_delta = 0.08`.

### Recursion Guardrails (call-level constraints)
Guardrails are enforced by `ai_recursive.RecursionManager` for any recursive
call site that opts into its API:

- **Termination condition is mandatory:** every call must supply a
  `termination_condition` string, or the call raises a
  `RecursionTerminationError`.
- **Hard ceilings:** `max_depth` and `max_children` are enforced per recursion
  root; exceeding either raises `RecursionLimitError`.
- **Cost budgeting:** `estimated_cost` is accumulated per root; exceeding
  `cost_budget` raises `RecursionBudgetError`.
- **Checkpoint gating:** when depth or cost exceed `checkpoint_ratio`, an
  optional `checkpoint_handler` is called and may deny continuation
  (`RecursionCheckpointError`).
- **Audit trail:** each call records an immutable snapshot containing
  `root_id`, `parent_id`, `depth`, `children_generated`, `cost_spent`,
  `budget_remaining`, `termination_condition`, and `timestamp`.

### Evaluation Metric Definitions
All metrics are deterministic and operate on the schema-aligned workflow dict.
`overall_score` is the arithmetic mean of all registered metric values.

- **clarity:** per phase, count words in `ai_task_logic` (fallback:
  `description`), compute `len(words) / 10`, clamp to `[0, 1]`, then average
  across phases.
- **coverage:** fraction of phases whose `ai_task_logic` or `description`
  contains non-empty text.
- **coherence:** redundancy estimate from `SemanticAnalyzer`, reported directly
  as coherence in `[0, 1]`.
- **specificity:** `min(1.0, avg_block_length / 500)`, where `avg_block_length`
  is average character length of extracted text blocks.
- **completeness:** average of (a) fraction of phases containing tasks and (b)
  fraction of tasks declaring both prerequisites/inputs and
  expected_outputs/outputs.
- **intent_alignment:** token overlap ratio between metadata intent fields
  (`purpose`, `description`, `title`) and all extracted content tokens, with
  stop-words removed.
- **usability:** fraction of tasks that define prerequisites/inputs,
  expected_outputs/outputs, and a description/action.

### Termination Conditions (evaluation-driven)
Evaluation-driven recursion stops when **any** of the following are true:

- **Depth cap reached:** `depth ≥ policy.max_depth`.
- **Insufficient improvement:** `score_delta < policy.min_improvement` **and**
  `semantic_delta < policy.min_semantic_delta`.
- **LLM decision does not permit refinement:** `llm_decision` is not
  `accept` or `revise`.

When the above conditions fail, the cycle returns the original workflow
snapshot without regenerating.

---

## 🏛 System Architecture

    sswg-mvm1.0/
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
- Audit bundles and promotion readiness gates
- Role-separated agents with documented creator/critic/curator hand-offs

---

## 🌀 Canonical 9-Phase Pipeline

sswg-mvm enforces the canonical phase order:

1. `ingest`
2. `normalize`
3. `parse`
4. `analyze`
5. `generate`
6. `validate`
7. `compare`
8. `interpret`
9. `log`

**Canonical run guide:** [docs/RUNBOOK.md](docs/RUNBOOK.md)

### Reproducible demo

Run the complete recursive pipeline (validation → evaluation → recursion → exports)
from the repo root with a single command:

```bash
python3 generator/main.py --demo --preview
```

Outputs land in `data/outputs/demo_run` and include:
- Refined workflow JSON + Markdown
- Mermaid + Graphviz diagrams
- Before/after metric plot (`metrics_before_after.svg`)
- Evaluation deltas and history snapshots

---

## 📄 Included Templates

| Template File                                 | Domain         | Purpose                                |
|----------------------------------------------|----------------|----------------------------------------|
| `campfire_workflow.json`                     | Storytelling   | Workshop-style workflow structures     |
| `creative_writing_template.json`             | Literary Arts  | Narrative & poetic workflow structures |
| `technical_procedure_template.json`          | Engineering    | SOP-style procedural workflows         |
| `meta_reflection_template.json`              | Metacognition  | Self-evaluating process frameworks     |
| `meta_reflection_unified_superframework.json`| Metacognition  | Unified superframework template        |
| `training_curriculum_template.json`          | Education      | Modular curriculum design structures   |

---

## 🛠 Setup & Usage

**Canonical run guide:** [docs/RUNBOOK.md](docs/RUNBOOK.md)

### Clone the Repository

    git clone https://github.com/Tommy-Raven/SSWG-mvm1.0.git
    cd SSWG-mvm1.0

### Install Dependencies
    use `pipx` if using virtual container
    `pip install -r REQUIREMENTS.txt`

### Validate the canonical PDL (required before runs)

    python3 -m generator.pdl_validator pdl/example_full_9_phase.yaml schemas

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


## 🔄 Automation & Gates

- `make doctor` for environment sanity checks
- `make test`, `make lint`, `make format` for local checks
- `make gates` for audit readiness and determinism validation
- `make preflight` for a local CI-equivalent sweep

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

**sswg-mvm is proprietary pre-release software.**  
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
  - **+tag** = specific os/development series. *Model versions appended first, no '+' symbol, OS versioning is non-hierarchal, and appended with an '+' symbol, i.e., > minimum viable model: 'mvm', Debian: '+deb', ChromeOS: '+cros', Transitive Semantic Version: 'ts', Deterministic Version: 'dtr', etc*
  - **yy** = iterative refinement/patch release  
- **Pre-release** (like `v0.0.9mvm`) = additional licensing restrictions apply.
