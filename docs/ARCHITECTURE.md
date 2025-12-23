Version: 1.0 (Canonical Architecture Reference)  
Last Updated: 2025-12-21  
Applies to: SSWG-MVM 1.x branch  

Status: Living document aligned to repository state

# SSWG-MVM Architecture

## Scope
This document describes the canonical architecture of the SSWG-MVM system as implemented in the SSWG-mvm1.0 repository.

It is intentionally code-first: all diagrams, subsystems, and execution flows reference real files and directories present in the repository. This document serves simultaneously as:
- a developer onboarding reference,
- a production architecture specification,
- and a research-grade system description.

---

## System Definition
SSWG-MVM (Synthetic Synthesist of Workflow Generation â€” Minimum Viable Model) is a schema-governed workflow generation and refinement system featuring:
- deterministic pipeline execution,
- formal validation against versioned schemas,
- semantic and quality evaluation,
- recursive refinement and expansion,
- memory-driven feedback loops,
- versioned lineage and diff tracking,
- visualization and export of artifacts,
- and reproducible execution via CI and environment locking.

---

## Subsystem Map (Responsibility Boundaries)

### Entry Surfaces
Provides user-facing and developer-facing invocation points.

- CLI:
  - cli/cli.py
  - ai_core/cli.py
  - config/cli.py
- Scripts / Utilities:
  - scripts/main.py
  - scripts/local_ci.py
  - scripts/check_templates.py
  - scripts/create_issues_from_json.py

---

### Core Orchestration
Orchestrates cross-module phase execution, dependency resolution, and workflow lifecycle control.

- ai_core/orchestrator.py
- ai_core/phase_controller.py
- ai_core/workflow.py
- ai_core/dependency_graph.py
- ai_core/module_registry.py

---

### Generator Pipeline
Executes the primary MVM workflow: validation, generation, evaluation, recursion, export, and history tracking.

- generator/main.py
- generator/workflow.py
- generator/modules.py
- generator/exporters.py
- generator/history.py
- generator/utils.py
- generator/performance_tracker.py

#### Recursion & Expansion
- generator/recursion_manager.py
- generator/recursive_expansion.py

#### Semantic & Evaluation Hooks
- generator/evaluation.py
- generator/semantic_scorer.py

---

### Evaluation & Metrics
Quantifies workflow quality and semantic improvement to guide recursion decisions.

- ai_evaluation/evaluation_engine.py
- ai_evaluation/quality_metrics.py
- ai_evaluation/scoring_adapter.py
- ai_evaluation/semantic_analysis.py

---

### Graph & Dependency Intelligence
Resolves dependencies, recursive flows, and semantic relationships between workflow components.

- ai_graph/dependency_mapper.py
- ai_graph/recursive_flow_graph.py
- ai_graph/semantic_network.py

---

### Memory / Feedback / Benchmarks
Persists snapshots, metrics, anomalies, and historical signals to enable adaptive behavior.

- ai_memory/memory_store.py
- ai_memory/feedback_integrator.py
- ai_memory/anomaly_detector.py
- ai_memory/benchmark_tracker.py

---

### Recursive Evolution / Version Control
Manages semantic diffs, variant generation, and lineage-aware workflow evolution.

- ai_recursive/version_control.py
- ai_recursive/version_diff_engine.py
- ai_recursive/merge_engine.py
- ai_recursive/variant_generator.py
- ai_recursive/memory_adapter.py

---

### Validation / Schema Governance
Enforces structural correctness and manages schema evolution across versions.

- ai_validation/schema_validator.py
- ai_validation/schema_tracker.py
- ai_validation/version_migrator.py
- ai_validation/regression_tests.py
- ai_validation/template_regression_tests.py

---

### Visualization & Export
Translates internal state into human-readable diagrams and artifacts.

- ai_visualization/export_manager.py
- ai_visualization/mermaid_generator.py
- ai_visualization/graphviz_adapter.py
- ai_visualization/markdown_importer.py

---

### Schemas (Contracts)
Defines the canonical structural and semantic contracts for workflows.

- schemas/workflow_schema.json
- schemas/module_schema.json
- schemas/phase_schema.json
- schemas/recursion_schema.json
- schemas/evaluation_schema.json
- schemas/semantics_schema.json
- schemas/metadata_schema.json
- schemas/ontology_schema.json
- schemas/template_schema.json

---

### LLM Adapter Layer
Abstracts model inference, enabling integration with local or API-based LLMs for refinement and meta-generation.

- modules/llm_adapter.py

This layer allows SSWG-MVM to remain model-agnostic while supporting LLM-in-the-loop recursion.

---

### Reproducibility & Packaging
Locks environments and execution conditions for replicable results.

- reproducibility/*
- docker/Dockerfile
- pyproject.toml
- REQUIREMENTS.txt

---

### Proof & Validation
Ensures correctness, regression safety, and execution stability.

- tests/test_generator_main.py
- tests/test_recursion.py
- tests/test_semantics.py
- tests/test_templates.py
- tests/test_versioning.py
- additional unit and integration tests under tests/

---

## Planned Evolution (Non-Binding)

| Module | Status | Purpose |
|------|------|------|
| ai_reasoning/ | future | Hybrid reasoning and semantic embedding management |
| ai_alignment/ | future | Reward tuning and recursion policy alignment |
| modules/agent_bridge.py | planned | Multi-agent LLM orchestration |
| meta_governance/ | roadmap | Formal recursion policy and safety constraints |

---

## Alignment Guarantees
- All subsystems correspond to real paths in the repository.
- No speculative modules are required for correctness.
- Any architectural change must update this document to remain canonical.
---

## Directory & File Mapping

* `ai_core/` — Orchestration and workflow phases
* `ai_recursive/` — Recursive generation, merging, memory, evaluation, registry
* `ai_memory/` — Persistent workflow storage and metrics
* `ai_evaluation/` — Quality assessment and feedback loops
* `generator/` — CLI and entry points
* `data/` — Templates and generated workflows
* `schemas/` — JSON schema validation
* `constitution/` — Rulebook enforcement
* `contradiction/` — Conflict detection and auto-remediation
* `reproducibility/` — Deterministic execution
* `safety/` — Sanitization, classification, sandbox simulation
* `web/` — FastAPI interface
* `tests/` — Automated testing

---

## Design Principles

* **Modularity:** Clear separation of orchestration, evaluation, validation, memory, and visualization
* **Recursive Design:** Self-learning workflows with iterative improvement
* **Traceable Outputs:** Versioned, archived, and human/machine-readable
* **Integration-Ready:** Seamless interaction with safety, constitution, and risk pipelines
* **Deployment-Ready:** CLI, containerization, and visualization support

