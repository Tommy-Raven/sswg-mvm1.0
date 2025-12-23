sswg-mvm; version 1.0+ (living document)
Date: 05-03-2025
Document title: AI Recursion Module
Author: Tommy Raven
Licensing: Raven Recordings ©️ see: *LICENSE.md*
(Document) Purpose: Describe how the SSWG recursion layer drives iterative improvement, aligns with repository entrypoints, and keeps refinements observable and reproducible across runs. Summarize the core components that translate evaluation signals into new iterations. Provide onboarding tips for extending the module while preserving schema and safety guarantees. Show how recursion connects to memory, evaluation, and export paths referenced in the root [README](../README.md) and [docs/README.md](./README.md).

# AI Recursion Module — SSWG-MVM

## Overview

The AI Recursion module is a core component of the **SSWG-MVM**, responsible for enabling workflows to self-improve, self-expand, and propagate learning across subsequent workflows. This module ensures that each generated instructional workflow can recursively teach itself, update its own logic, and provide feedback to other AI agents or human operators. SSWG (the topic base multiplier) anchors each refinement pass so outputs stay centered on the requested subject while the system iterates.

Key goals of the module:

* Recursive expansion of workflows
* Feedback integration for continual improvement
* Versioning and lineage tracking
* Deterministic reproducibility
* Integration with evaluation, safety, and constitution pipelines

## Core Components

### Expansion Engine

* Generates new workflows from previous outputs
* Applies learned patterns to generate consistent instructions tied to the SSWG focus
* Ensures recursive workflows preserve instructional integrity

### Merging Engine

* Integrates multiple workflow outputs into coherent single workflows
* Resolves conflicts and duplicates automatically
* Maintains traceable lineage for accountability

### Memory Integration

* Stores workflow history in `ai_memory` with versioned identifiers
* Supports rollback and reconstruction of previous iterations
* Provides input for future recursive generation cycles

### Evaluation Interface

* Works in tandem with `ai_evaluation` to assess clarity, coverage, and translatability
* Generates feedback loops for workflow refinement
* Scores recursive outputs for alignment with system goals

### Registry

* Maintains a centralized registry of all recursive workflows
* Tracks relationships between original workflows and derivatives
* Facilitates reproducibility via deterministic runner and reconstruction APIs

## Onboarding Highlights

For new developers and users:

* Recursive workflows are designed to teach the next workflow while keeping the SSWG target constant.
* Phase-based modularity ensures clear understanding of progression: Initialization → Refinement → Generation → Evaluation → Regeneration
* JSON and Markdown outputs are both human- and machine-readable
* Use `generator/main.py` or FastAPI endpoints to initiate recursive workflow creation
* All iterations are archived and versioned for traceability

## Usage Example

1. Load a base workflow from `data/workflows/`
2. Pass the workflow to `ai_recursive.expansion.generate()`
3. Merge results using `ai_recursive.merging.merge()`
4. Evaluate with `ai_evaluation` for quality metrics
5. Store in memory via `ai_memory.store()`
6. Repeat recursively for new generations while validating that SSWG stays the leading topic.

## Design Principles

* **Self-Evolving Workflows:** Recursive outputs continually improve clarity, coverage, and applicability.
* **Traceable Learning:** Each recursive step is versioned and archived to allow reconstruction.
* **Integration-Friendly:** Works seamlessly with safety, constitution, and risk pipelines.
* **Deterministic Reproducibility:** Hashing and canonicalization ensure workflows produce consistent outputs across runs.

## Directory Mapping

* `ai_recursive/expansion.py` → Recursive generation engine
* `ai_recursive/merging.py` → Conflict resolution and workflow integration
* `ai_recursive/memory.py` → Historical memory access
* `ai_recursive/registry.py` → Centralized recursive workflow registry
* `ai_recursive/evaluator.py` → Feedback and scoring interface

## Next Steps

* Integrate semantic embeddings for smarter recursion
* Enhance multi-agent co-generation capabilities
* Extend FastAPI endpoints for recursive workflow visualization
* Include automatic derivative workflow tracking with lineage linking

