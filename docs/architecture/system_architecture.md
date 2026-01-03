---
anchor:
  anchor_id: docs_architecture_system_architecture
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

sswg-mvm; version 1.0+ (living document)
Date: 05-03-2025
Document title: System Architecture
Author: Tommy Raven
Licensing: Raven Recordings ©️ see: *LICENSE.md*
(Document) Purpose: Summarize the layered architecture of the SSWG-MVM, showing how schema enforcement, recursion, memory, and evaluation connect. Provide pointers back to the root [README](../../README.md) and [docs/README.md](../README.md) for navigation. Clarify how SSWG anchors each module so refinement cycles stay on-topic.

# 🏛 System Architecture
### SSWG-MVM — Synthetic Synthesist of Workflow Generation

sswg-mvm organizes itself as a **layered modular architecture**, balancing strict schema-driven control with dynamic recursive refinement.

---

# 🧩 High-Level Architecture

```
           ┌────────────────────────────────────────┐
           │              CLI / API Layer            │
           └────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                    Generator Engine (MVM)                │
│  - main pipeline                                         │
│  - refinement (RecursionManager)                         │
│  - dependency autocorrect                                │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                     Validation Layer                      │
│  - jsonschema                                             │
│  - metadata + phase requirements                          │
│  - DAG structural checks                                   │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                     Evaluation Layer                      │
│  - Clarity metrics                                        │
│  - semantic scoring (future)                              │
│  - phase/task density                                     │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                Memory & Versioning Subsystem             │
│  - feedback integrator                                    │
│  - lineage tracking                                        │
│  - regeneration triggers                                   │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                   Visualization Layer                     │
│  - Mermaid (Markdown diagrams)                             │
│  - Graphviz planned                                        │
└──────────────────────────────────────────────────────────┘
```

---

# ⚙ Design Principles

### **1. Deterministic core**
Valid workflows must always meet schema validation invariants:  
- metadata correctness  
- phase order  
- dependency graph validity  

Canonical invariants are defined in [invariants.yaml](../../invariants.yaml) and expanded in [root_contract.yaml](../../root_contract.yaml).

### **2. Recursive refinement**
The MVM includes a *minimal recursion engine* designed to:

- detect weak phases  
- restructure task order  
- annotate missing metadata  
- apply consistent formatting  

### **3. Schema supremacy**
All templates and generated workflows respect:

```
schemas/workflow_schema.json
```

This enables:

- automated testing  
- schema validation invariants  
- version bump automation in CI  

### **4. Minimal external dependencies**  
Only standard Python + jsonschema + optional Graphviz.

---

# 🧠 Component Map

| Subsystem | Directory | Purpose |
|-----------|-----------|---------|
| Core | `ai_core` | Orchestration, pipeline glue |
| Recursive | `ai_recursive` | Diff engine, refinement |
| Validation | `ai_validation` | Workflow schema, consistency checks |
| Evaluation | `ai_evaluation` | Scores, metrics |
| Memory | `ai_memory` | Long-term feedback + lineage |
| Visualization | `ai_visualization` | Graphs + Mermaid |
| Generator | `generator` | Main execution engine |

---

# 📦 How Components Communicate

```
User → CLI → MVM Pipeline
MVM → Validator → Graph → Evaluator → Recursive Refinement
Refined Workflow → Exporters → Memory/History
```

Each workflow run produces:

- JSON artifact  
- Markdown artifact  
- optional Mermaid DAG  
- lineage entry  

---

# 🔮 Future Architecture Extensions

- Multi-agent workflow analysis  
- Parallel recursive branches  
- Metaphorical “grimoire pages” (plugin-based expansions)  
- GraphQL API layer

---

# 🧬 v1.2.0 Cognitive Stack (Extended)

The bounded cognition update introduces two additional layers that sit above the core execution loop.

```
           ┌────────────────────────────────────────┐
           │              CLI / API Layer            │
           └────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                    Cognitive Core (MVM)                  │
│  - schema-governed recursion                              │
│  - phase enforcement                                      │
│  - deterministic evaluation                               │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                   Optimization Subsystem                 │
│  - ontology alignment                                     │
│  - deterministic telemetry                                │
│  - verity tensor inputs                                   │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                 Entropy Governance Layer                 │
│  - entropy budgets                                        │
│  - bounded cognition termination                          │
│  - verity/entropy convergence checks                      │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                Memory & Versioning Subsystem             │
│  - lineage tracking                                        │
│  - telemetry capture                                       │
│  - benchmark evolution                                     │
└──────────────────────────────────────────────────────────┘
```

This extended stack preserves existing deterministic guarantees while clarifying how optimization and entropy governance gate recursion at v1.2.0.
