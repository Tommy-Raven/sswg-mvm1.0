> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

---
anchor:
  anchor_id: docs_contributor_guide
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

sswg-mvm; version 1.0+ (living document)
Date: 05-03-2025
Document title: Contributor Guide
Author: Tommy Raven
Licensing: Raven Recordings ©️ see: *LICENSE.md*
(Document) Purpose: Help new contributors onboard to the SSWG-MVM by outlining setup, project structure, coding standards, and support channels. Reinforce that SSWG is the topic base multiplier guiding recursive refinement. Direct readers to the root [README](../README.md) and [docs/README.md](./README.md) for system entrypoints and navigation.

# Contributor Guide — SSWG-MVM

## Welcome

Welcome to the **SSWG-MVM**, an AI instructional workflow generator anchored on the SSWG topic base multiplier. This guide helps new contributors onboard quickly, understand the system architecture, and follow best practices for development, testing, and contribution.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Coding Guidelines](#coding-guidelines)
5. [Testing & CI](#testing--ci)
6. [Contribution Process](#contribution-process)
7. [Onboarding Highlights](#onboarding-highlights)
8. [Contact & Support](#contact--support)

---

## Getting Started

### Prerequisites

* Python 3.10+
* pip
* Optional: Graphviz for workflow visualization
* GitHub account for contribution and issue tracking

### Installation

Clone the repository:

git clone [https://github.com/Tommy-Raven/sswg-mvm1.0.git](https://github.com/Tommy-Raven/sswg-mvm1.0.git)
cd sswg-mvm1.0

Install dependencies:

pip install -r requirements.txt

Run the development FastAPI server:

uvicorn src.web.app:app --reload

Run CLI examples:

python3 generator/main.py --purpose "Design an AI ethics curriculum"

Generated workflows appear in `data/workflows/` and logs in `logs/workflow.log`.

---

## Project Structure

* `/ai_conductor/` — Core workflow orchestration, module management, and phases
* `/ai_recursive/` — Recursive generation and self-improving workflow routines tuned to SSWG
* `/ai_memory/` — Persistent memory, version history, and lineage tracking
* `/ai_evaluation/` — Evaluation metrics: clarity, coverage, expandability, translatability
* `/generator/` — CLI interface for workflow creation
* `/data/templates/` — Workflow archetypes (training, technical, creative, meta-reflection)
* `/data/workflows/` — Generated workflows (human-readable and JSON-minified)
* `/schemas/` — JSON schemas enforcing module and workflow integrity
* `/tests/` — Unit, integration, and acceptance tests
* `/docs/` — Documentation and system references

Core layers also include:

* Constitution engine (rules & predicates)
* Safety stack (sanitization & sandbox simulation)
* Contradiction detection and auto-remediation
* Deterministic execution and reproducibility
* Risk pipeline with weighted workflow scoring

---

## Development Workflow

1. Fork the repository and create a feature branch.
2. Follow coding guidelines for style, naming, and docstrings.
3. Implement your feature or fix, ensuring it passes existing unit tests.
4. Run integration and acceptance tests to validate workflow end-to-end.
5. Commit changes with meaningful messages.
6. Submit a pull request for review.

---

## Coding Guidelines

* Python 3.10+ syntax
* PEP 8 compliant
* Type hints for functions and methods
* Docstrings for all modules, classes, and functions
* Modular design: new workflows or features should live in the appropriate package

---

## Testing & CI

* Unit tests: `tests/unit/`
* Integration tests: `tests/integration/`
* End-to-end acceptance tests: `tests/integration/test_end_to_end_goal_to_publish.py`
* Run tests:

pytest -v tests/

CI/CD uses GitHub Actions to enforce tests, code linting, and deployment checks.

---

## Contribution Process

* Open an issue for bugs, features, or enhancements.
* Reference your issue in your pull request.
* Ensure all code passes tests before PR submission.
* Use descriptive commit messages and follow branch naming conventions.

---

## Onboarding Highlights

* Understand the recursive workflow: each output can feed the next workflow while keeping SSWG stable.
* Workflows are bimodal: Markdown for humans, JSON for machines.
* Schema-driven validation ensures consistency.
* Safety and constitution engines maintain policy compliance.
* Use the deterministic runner for reproducible workflow execution.
* All phases are modular, versioned, and traceable through the archivist and memory system.

---

## Contact & Support

* GitHub Issues preferred for questions or support.
* Author: Tommy Raven
* Repository: [github.com/Tommy-Raven/sswg-mvm1.0](https://github.com/Tommy-Raven/sswg-mvm1.0)
* Codename: SSWG-MVM
