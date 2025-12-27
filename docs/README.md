# SSWG-MVM (SSWG Skeleton)

SSWG-MVM (Synthetic Synthesist of Workflow Generation â€” Minimum Viable Model) is a **meta-educational AI system** for generating, evaluating, and evolving both AI- and human-formatted instructional workflows.

This repository represents the **canonical skeleton and reference implementation** of the SSWG MVM: a schema-governed, recursively evaluative workflow generation system designed for reproducibility, extensibility, and research-grade introspection.

The system combines deterministic pipeline execution with semantic evaluation, recursive refinement, and memory-driven feedback loops to demonstrate **self-improving instructional and procedural workflow synthesis**.

---

## Canonical Runbook

**Primary entrypoint (how to run + expected outputs):**  
RUNBOOK.md

Other docs are secondary/overview and should defer to this canonical runbook to avoid drift.

---

## What This Repository Is

This repository serves as the **canonical skeleton** for SSWG-MVM.

It defines:
- the immutable base structure of the system,
- core orchestration and generation scaffolding,
- schema contracts and validation rules,
- and placeholder or evolving modules for modular, recursive AI instructional workflows.

All downstream projects, forks, and experimental branches are expected to inherit from or reference this structure.

---

## Architecture

The authoritative, code-aligned architecture reference lives here:

docs/ARCHITECTURE.md

This document functions as:
- the canonical system architecture specification,
- a developer onboarding guide,
- and a research-grade technical reference aligned directly to repository source.

All architectural claims in this project are grounded in executable code and validated by automated tests.

---

## Repository Structure (High-Level)

generator/      Core MVM workflow generator and recursion engine  
cli/            Command-line interface for workflow execution and governance  
pdl/            Phase Definition Language (PDL) files defining workflow phases  
schemas/        Canonical schema contracts (workflow, phase, recursion, evaluation)  
ai_core/        Core orchestration, workflow lifecycle, and phase control  
ai_evaluation/ Semantic and quality evaluation engines  
ai_graph/       Dependency and semantic graph intelligence  
ai_memory/      Feedback, benchmarking, and persistence  
ai_recursive/   Versioning, diffs, and evolutionary refinement  
ai_validation/  Schema governance and regression safety  
ai_visualization/ Diagram and artifact generation  
artifacts/      Additive-only generated artifacts  
docs/           Documentation and usage guides  
reproducibility/ Environment locking and CI alignment  

---

## Purpose

This repository exists to:

- Provide a **stable, immutable base** for SSWG workflows.
- Enable **branch and fork governance** for all edits beyond canonical modules.
- Define **modular phase-execution scaffolds** for PDL-based AI workflows.
- Serve as the reference structure for **all SSWG MVM operations, rebuilds, and research**.
- Demonstrate recursive, evaluative workflow generation in a reproducible and inspectable manner.

---

## Getting Started

1. Clone the canonical repository:

   git clone https://github.com/Tommy-Raven/SSWG-mvm1.0.git

2. Explore the folder structure and documentation under docs/.

3. Follow the canonical run guide:

   docs/RUNBOOK.md

4. Run or inspect the demo pipeline described in:

   docs/ARCHITECTURE.md  
   docs/QUICKSTART.md

4. Use this repository as the base for:
   - additive artifact creation,
   - phase-based PDL execution,
   - recursive workflow experimentation,
   - research or educational extensions.

---

## Governance Notes

- Do not modify the canonical branch directly.
- Use branches or forks for any experimental or downstream development.
- Core orchestration and schema contracts should evolve only through deliberate, reviewed changes.
- Generated artifacts must remain additive-only.

---

## Status

SSWG-MVM is an actively evolving research and engineering system.

The current focus (Phase I) is on:
- architectural clarity,
- reproducibility,
- demonstrable recursive improvement,
- and LLM-in-the-loop integration.

---

## License

See LICENSE for details.
