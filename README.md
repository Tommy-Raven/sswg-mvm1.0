# SSWG-MVM v1.0.2
SSWG — SYNTHESIST OF WORKFLOW GENERATION (MANDATED VERITY MINDSET)

<div align="center">
  <img src="raven.svg" width="180" alt="Raven Recordings Logo">
</div>

<div align="center">

![STATUS](https://img.shields.io/badge/STATUS-ACTIVE-7E3ACE?style=for-the-badge)
![BUILD](https://img.shields.io/badge/BUILD-STABLE-4B9CD3?style=for-the-badge)
![VERSION](https://img.shields.io/badge/VERSION-1.0.2-9E3CE7?style=for-the-badge)
![PYTHON](https://img.shields.io/badge/PYTHON-3.10%2B-blue?style=for-the-badge&logo=python)
![ARCHITECTURE](https://img.shields.io/badge/ARCHITECTURE-DETERMINISTIC_RECURSIVE-black?style=for-the-badge)
![LICENSE](https://img.shields.io/badge/LICENSE-PROPRIETARY-black?style=for-the-badge)

</div>

sswg-mvm is the Minimum Viable Model implementation of SSWG — Synthesist of Workflow Generation operating under the Mandated Verity Mindset (MVM).

It is a deterministic, governance-bound workflow synthesis engine designed to generate structured, auditable, multi-phase workflow systems. The system does not produce conversational output and does not execute operational logic. All outputs are non-operational artifacts intended for inspection, validation, and audit.

Status: Active  
Version: v1.0.2  
Architecture: Deterministic, Bounded Recursive  
License: Proprietary  

---

LEGAL STATUS

sswg-mvm is proprietary software.
Evaluation is permitted under license.
Redistribution, resale, hosting, derivative systems, dataset extraction, and model or agent training are prohibited unless explicitly authorized.

Authoritative terms are defined in LICENSE.md and TERMS_OF_USE.md.

---

OVERVIEW

sswg-mvm is the Minimum Viable Model of SSWG — Synthesist of Workflow Generation, operating under the Mandated Verity Mindset.

The system synthesizes structured workflow systems rather than responses. It produces deterministic artifacts that describe processes, dependencies, and evaluation logic in a form suitable for governance review and reproducibility analysis.

Primary outputs include:
- Multi-phase workflow specifications
- Deterministic dependency graphs (DAGs)
- Schema-validated JSON artifacts
- Versioned lineage and comparison records
- Bounded recursive refinements

All generation is non-operational and governance-bounded.

Author: Tommy Raven (Thomas Byers)  
Copyright © Raven Recordings 2025–2026  

---

CANONICAL RUNBOOK

The canonical operational reference is:

docs/RUNBOOK.md

All other documentation is explicative only and must defer to the runbook and to authoritative TOML governance documents located under directive_core/docs.

---

SYSTEM DESIGN PRINCIPLES

Determinism  
Given identical inputs, versions, and governance state, outputs are reproducible and auditable.

Governance First  
All system behavior is constrained by TOML governance artifacts loaded through the constitutional ingestion sequence defined by SSWG_CONSTITUTION.toml.

Bounded Recursion  
Recursive refinement is explicitly gated, depth-limited, cost-bounded, and fully auditable.

Schema Discipline  
All workflows are validated against canonical schemas prior to acceptance.

Lineage and Traceability  
Each refinement produces immutable evidence artifacts suitable for audit, comparison, and review.

---

FORMAL RECURSION AND EVALUATION SEMANTICS (REFERENCE)

This section describes implemented behavior. Authoritative guarantees and non-guarantees are defined in FORMAL_GUARANTEES.toml.

Recursion Cycle:
1. Baseline workflow evaluation using deterministic metrics
2. Candidate refinement proposal
3. Candidate re-evaluation
4. Delta computation (score delta and semantic delta)
5. Acceptance gating against defined thresholds
6. Evidence and lineage recording

Default bounds:
- max_depth = 2
- min_improvement = 0.05
- min_semantic_delta = 0.08

Guardrails:
- Explicit termination condition required
- Hard recursion depth ceilings
- Cost budgeting enforced
- Checkpoint gating supported
- Immutable audit snapshot recorded per call

---

SYSTEM ARCHITECTURE (REFERENCE VIEW)

sswg-mvm/
- generator/            Primary orchestration engine
- ai_recursive/         Bounded recursion logic
- ai_validation/        Schema and invariant enforcement
- ai_graph/             Dependency graph construction
- ai_evaluation/        Deterministic quality metrics
- ai_memory/            Lineage and version tracking
- ai_visualization/     Diagram exporters
- data/templates/       Seed workflow templates
- schemas/              Canonical JSON schemas
- directive_core/docs/  Authoritative TOML governance

---

CORE CAPABILITIES

- Template-driven workflow synthesis
- Deterministic recursive refinement
- Strict schema enforcement
- Dependency graph validation
- Versioned evidence bundles
- Lineage comparison and diffing
- CLI-driven execution
- Governance-gated behavior

---

OPERATIONAL PIPELINE (CONCEPTUAL)

1. Template ingestion
2. Normalization and schema validation
3. Dependency graph construction
4. Bounded recursive refinement
5. Artifact emission (JSON and diagrams)
6. Lineage and evidence recording

Operational authority is defined by docs/RUNBOOK.md.

---

INCLUDED TEMPLATES (EXAMPLES)

creative_writing_template.json  
technical_procedure_template.json  
meta_reflection_template.json  
training_curriculum_template.json  

---

SETUP AND USAGE (REFERENCE)

git clone https://github.com/Tommy-Raven/sswg-mvm.git  
cd sswg-mvm  
pip install -r requirements.txt  
python generator/main.py --template creative --preview  

Artifacts are written to data/outputs/ and include workflow JSON, diagrams, metric summaries, and lineage snapshots.

---

TESTING

pytest -v

Test coverage includes governance enforcement, schema validation, recursion bounds, determinism replay, and end-to-end generation.

---

CI AND AUTOMATION

Implemented:
- Determinism replay tests
- Governance ingestion validation
- Promotion readiness checks

---

AUTHOR

Tommy Raven  

Systems Architect 

Raven Recordings, LLC  

GitHub: https://github.com/Tommy-Raven  

Pronouns: Apache / Helicopter  
Clarification: Not an actual helicopter. Still airborne intellectually.

---

LICENSE SUMMARY

sswg-mvm is proprietary software.
Evaluation only. No redistribution, hosting, training, or derivative works.

---

VERSIONING NOTES

v1.x.y indicates canonical governance-aligned releases.
MVM denotes Mandated Verity Mindset lineage.
Deterministic and transitive tags apply per governance.

---

STATUS

Phase 000 complete.
Governance is canonical, ingestion is deterministic, and authority is singular.
Phase 001 may proceed.
