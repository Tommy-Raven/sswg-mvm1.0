---
anchor:
  anchor_id: contributing
  anchor_version: "1.1.0"
  scope: documentation
  owner: sswg
  status: draft
---

sswg-mvm (living document)
Last updated: 2025-03-01
Document title: CONTRIBUTING.md
Author: Tommy Raven
Licensing: Raven Recordings ©️ see: *LICENSE.md*
(Document) Purpose: Provide a clear pathway for contributing to the sswg-mvm stack, clarifying scope, expectations, and review cadence. Outline how proposals connect to the repo overviews in README.md and docs/README.md. Ensure newcomers know where to start, how to coordinate changes, and what quality bars keep releases stable.

# Contributing to sswg-mvm

The root [README.md](./README.md) and [docs/README.md](./docs/README.md) describe the system surface area and entrypoints. This guide focuses on how to add to that surface responsibly while keeping the recursion, evaluation, and telemetry stacks stable.

## Contribution scope
- **Recursive orchestration and DAG management** — refinements to the recursion engine, graph validators, and workflow schemas.
- **Memory, lineage, and logging** — extensions to evolution logs, telemetry pipelines, or provenance capture.
- **Evaluation and semantics** — new scoring functions, semantic delta checks, or benchmarking harnesses.
- **Plugins and integrations** — safely extending behavior via the hooks in `docs/PLUGIN_DEVELOPMENT.md`.
- **Docs and community health** — clarifying guides, adding examples, or improving onboarding material.

## Ground rules
- Follow the [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) and security expectations in [SECURITY.md](./SECURITY.md).
- Respect canonical layers (`generator/`, `cli/`, `pdl/`, `reproducibility/`) and additive-only layers (`artifacts/`, `data/`, `docs/`).
- Align change descriptions with the architecture maps in [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) and the recursion overview in [docs/RECURSION_MANAGER.md](./docs/RECURSION_MANAGER.md).
- Prefer small, reviewable PRs. Pair large refactors with a short design doc or checklist linked from the PR body.
- Keep imports clean—no `try/except` wrappers around imports per project conventions.

## Getting started
1. Read the root [README.md](./README.md) to understand goals and boundaries.
2. Skim [docs/README.md](./docs/README.md) for documentation structure and navigation.
3. Run local setup using `python3 -m venv .venv && source .venv/bin/activate && pip install -r REQUIREMENTS.txt`.
4. Validate the canonical PDL before running workflows:
   `python3 -m generator.pdl_validator pdl/example_full_9_phase.yaml schemas`.
5. Execute relevant smoke tests or linting before opening a PR.

## Change workflow
- **Issues:** Open issues with a concise problem statement and reproduction when applicable. Tag modules (`ai_recursive`, `ai_memory`, `ai_monitoring`, etc.).
- **Branches:** Use meaningful branch names (e.g., `feat/telemetry-sinks` or `fix/semantic-thresholds`).
- **Commits:** Write descriptive messages that reference impacted modules and primary behavior changes.
- **Reviews:** Expect feedback on test coverage, documentation updates, and cross-cutting impacts (telemetry, evolution logging, semantic scoring).
- **Docs:** When adding features, update linked guides such as [docs/EVOLUTION_LOGGING.md](./docs/EVOLUTION_LOGGING.md) or [docs/TELEMETRY_GUIDE.md](./docs/TELEMETRY_GUIDE.md) so navigation stays accurate.

## Testing and quality bars
- Prefer deterministic tests. When randomness is required, seed it and document the seed in test fixtures.
- Validate recursion and graph changes against schemas in `schemas/`.
- For new metrics or semantic functions, add examples to `ai_evaluation` and cross-reference in [docs/SEMANTIC_ANALYSIS.md](./docs/SEMANTIC_ANALYSIS.md).
- Keep logs and telemetry consistent with the patterns in `ai_monitoring` and the dashboards described in [docs/TELEMETRY_GUIDE.md](./docs/TELEMETRY_GUIDE.md).

## Communication
- For questions, use GitHub Discussions or the issue tracker (user: **@Tommy-Raven**).
- Include reproduction details and environment notes (OS, Python version) when reporting bugs.
- Celebrate wins by adding notable improvements to `CHANGELOG.md` when applicable.
