sswg-mvm; version 1.0+ (living document)
Date: 05-03-2025
Document title: API Reference
Author: Tommy Raven
Licensing: Raven Recordings ©️ see: *LICENSE.md*
(Document) Purpose: Summarize the primary programmatic interfaces for the SSWG-MVM. Show how to create, refine, and persist workflows while respecting schema and safety constraints. Provide quick examples that keep the SSWG topic base multiplier centered in recursive passes. Point readers back to the root [README](../README.md) and [docs/README.md](./README.md) for navigation.

# API Reference — SSWG-MVM

## Overview

The API provides programmatic access to the **SSWG-MVM** workflow generation, evaluation, recursion, and memory systems. It enables developers to initiate workflows, evaluate their quality, recursively refine outputs, and interact with stored workflow histories. The API is designed to support both human-readable and machine-readable outputs and integrates seamlessly with safety, constitution, and risk pipelines while ensuring the SSWG target remains stable through iterations.

## Main Classes & Functions

| Module                            | Class / Function                      | Description                                                         |
| --------------------------------- | ------------------------------------- | ------------------------------------------------------------------- |
| `generator.main`                  | `create_workflow(user_params)`        | Initializes the full workflow pipeline from high-level goals.       |
| `generator.recursion_manager`     | `run_cycle(workflow)`                 | Executes recursive generation, feedback integration, and evolution. |
| `ai_core.workflow`                | `assemble(phases, modules)`           | Constructs workflows from phase definitions and modular components. |
| `ai_core.registry`                | `register(workflow_id, workflow_obj)` | Adds workflow metadata to the centralized registry.                 |
| `ai_evaluation.semantic_analysis` | `compare(reference, candidate)`       | Computes semantic delta score between workflows.                    |
| `ai_monitoring.telemetry`         | `record(event_type, metadata)`        | Logs events, metrics, and recursion performance.                    |
| `ai_memory.store`                 | `save(workflow)`                      | Archives versioned workflow for traceable lineage.                  |
| `ai_recursive.expansion`          | `generate(base_workflow)`             | Creates new workflows based on previous outputs.                    |
| `ai_recursive.merging`            | `merge(workflows)`                    | Resolves conflicts and combines workflows.                          |
| `ai_recursive.evaluator`          | `score(workflow)`                     | Provides feedback on clarity, coverage, and translatability.        |

## Example API Calls

```python
from generator.main import create_workflow
from ai_recursive.expansion import generate
from ai_evaluation.semantic_analysis import compare
from ai_memory.store import save

# Step 1: Create initial workflow
workflow = create_workflow(user_params)

# Step 2: Generate recursive expansions
expanded_wf = generate(workflow)

# Step 3: Evaluate semantic quality
score = compare(workflow, expanded_wf)

# Step 4: Store workflow in memory for lineage tracking
save(expanded_wf)
```

## Onboarding Highlights for API Users

* Start with `generator.main.create_workflow()` to define workflows from user intent.
* Recursive improvements are triggered via `generator.recursion_manager.run_cycle()`.
* Evaluation metrics include clarity, coverage, expandability, and AI translatability.
* Use `ai_memory` functions to archive workflows for reproducibility and reconstruction.
* All outputs are compatible with FastAPI endpoints for web integration.

## Best Practices

* Always validate user input through the **Constitution Engine** before execution.
* Integrate **Safety Stack** checks (`safety_classifier`, `sandbox_simulator`) for untrusted inputs.
* Leverage versioning from `ai_recursive.registry` to maintain traceable workflow history.
* Combine evaluation scores with feedback loops to guide recursive improvements.

