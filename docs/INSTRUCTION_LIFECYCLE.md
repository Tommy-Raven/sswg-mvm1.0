---
anchor:
  anchor_id: docs_instruction_lifecycle
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

sswg-mvm; version 1.0+ (living document)
Date: 12-23-2025
Document title: Instruction Lifecycle
Author: Tommy Raven
Licensing: Raven Recordings ©️ see: *LICENSE.md*
(Document) Purpose: Define a universal lifecycle for instructions so creative artifacts move predictably from conception to retirement without conflicting versions or endless iteration. Establishes states, promotion gates, deprecation rules, and lineage safeguards aligned to the SSWG-MVM recursion and evaluation stack.

# Instruction Lifecycle — SSWG-MVM

## Overview

Instruction artifacts (schemas, prompts, workflows, playbooks, or policies) should evolve through explicit stages so teams can distinguish draft explorations from canonical guidance. This lifecycle sets the allowed states, promotion criteria, freezing rules, and archival expectations to prevent contradictory directions and to maintain historical traceability.

## Lifecycle states

| State      | Description | Entry requirements | Exit conditions | Allowed transitions |
| ---------- | ----------- | ------------------ | --------------- | ------------------- |
| **Draft**  | Exploratory instruction under active iteration. | Issue or request recorded; scope defined; owner assigned. | Meets validation gates for promotion; linked tests or exemplars captured. | Draft → Tested; Draft → Archived (if abandoned). |
| **Tested** | Instruction has been exercised in controlled runs with evidence. | Draft artifacts validated against schemas; at least one reproducible run with metrics logged. | Maintains stability across two consecutive runs; reviewers sign off on clarity and risk. | Tested → Canonical; Tested → Draft (if defects found); Tested → Archived (if superseded). |
| **Canonical** | Authoritative guidance used by default in pipelines and documentation. | Promotion ticket cites test evidence; version tag assigned; references wired into relevant modules/docs. | Replacement canonical approved or deprecation initiated; lineage anchors captured. | Canonical → Archived (when superseded); Canonical → Draft (only via formal revision request with new version ID). |
| **Archived** | Retired instruction retained for lineage and audit. | Decommission decision recorded with rationale; replacement (if any) linked. | None; archived items are immutable snapshots. | Archived → Draft (only by explicit resurrection ticket with new version lineage). |

## Promotion and freezing rules

- **Draft → Tested**
  - Minimum: schema validation passes, scope is stable, and acceptance criteria are written.
  - Explainability: produce an MVM explainability layer (assumptions + scope, invariants, major decision rationale, evidence summary, failure map).
  - Evidence: attach at least one reproducible run (logs, metrics, or rendered artifacts) demonstrating the intended behavior.
  - Ownership: a maintainer or domain lead accepts stewardship for the test window.

- **Tested → Canonical**
  - Reliability: two consecutive green runs in representative environments; failure cases documented.
  - Explainability: validate that explainability fields are complete, tagged (verified / empirical / heuristic / speculative), and include provenance + confidence.
  - Transfer checks: complete at least one transfer or debug test with a downstream agent to confirm scope and invariant interpretation.
  - Review: peer review for clarity, safety, and alignment with platform constraints (schemas, recursion controls, evaluation harnesses).
  - Traceability: assign a version ID, update cross-references (schemas, CLI help, docs), and note any deprecated predecessors.

- **Freezing Canonical**
  - Canonical instructions are immutable except through a revision request that spawns a new **Draft** with an incremented version.
  - Emergency edits must include a retroactive incident record and immediate revalidation.

- **Deprecation and archival**
  - Trigger: a superior instruction reaches **Canonical** or the previous guidance is unsafe/obsolete.
  - Action: mark the old canonical as **Archived**, annotate the successor link, and remove it from defaults and templates.
  - Preservation: archive retains metadata (author, version, dates, decision record) and referenced artifacts.

## Cross-agent explainability requirements (MVM)

Explainability must be treated as a first-class artifact for instruction promotion and reuse. Each Tested or Canonical instruction must include a minimal, structured explainability layer with the following fields:

- **Assumptions + scope:** state the intended context, required tools/resources, and explicit non-applicability boundaries.
- **Invariants:** list constraints that must remain true after adaptation (e.g., safety checks, ordering, evaluation gates).
- **Decision rationale:** capture major choices with drivers, tradeoffs, and triggers (conditions that would change the decision).
- **Evidence summary:** list evaluation signals, provenance, confidence tags, and last-validated version/timestamp.
- **Failure map:** typical failure modes, detection signals, likely causes, and remediation/escalation steps.

Optional explainability layers can add deeper causal chains, alternative architectures, or historical evolution narratives, but must never replace the minimal layer above.

## Explainability evaluation

Explainability quality is assessed with agent-centered tests:

- **Transfer test:** can a downstream agent adapt the artifact to a new domain without breaking invariants?
- **Debug test:** can a downstream agent diagnose a seeded failure using the explainability layer alone?
- **Scope test:** can a downstream agent correctly state where the method should not be used?
- **Consistency test:** do multiple agents interpret core constraints the same way?

If these tests fail, the instruction remains in **Draft** or **Tested** until the explainability layer is repaired.

## Change management workflow

1. **Propose** — File a change request identifying scope, risks, and intended success metrics; create or update the Draft with owners.
2. **Test** — Run controlled evaluations (unit tests, simulations, or dry runs) and attach metrics/logs in the recursion memory store.
3. **Review** — Peer review for correctness, clarity, bias/safety, and schema alignment; resolve conflicts against existing canonicals.
4. **Publish** — Promote to **Canonical**, broadcast location updates (docs, schemas, CLI help), and tag the version.
5. **Retire** — When superseded, archive the prior canonical with pointers to its successor and any migration notes.

## Lineage and provenance

- Record every state change with timestamps, approvers, and rationale in the evolution log (see [docs/EVOLUTION_LOGGING.md](./EVOLUTION_LOGGING.md)).
- Use deterministic version IDs and parent-child links so recursive generations can cite the instruction they followed.
- Store runnable exemplars and evaluation metrics alongside each Tested or Canonical record to make reruns verifiable.
- Keep human-readable summaries in docs while persisting machine-friendly metadata in the memory store for audits.

## Operational checklists

- **Before promoting to Tested:**
  - [ ] Scope and acceptance criteria written
  - [ ] Schema validation clean
  - [ ] MVM explainability layer drafted (assumptions/scope, invariants, rationale, evidence, failure map)
  - [ ] Reproducible run captured with metrics

- **Before promoting to Canonical:**
  - [ ] Two consecutive green runs
  - [ ] Explainability tags include provenance, confidence, and validation timestamp
  - [ ] Transfer or debug test completed with a downstream agent
  - [ ] Peer review complete
  - [ ] Version ID assigned and references updated

- **Before Archiving a Canonical:**
  - [ ] Successor (if any) linked
  - [ ] Decision rationale recorded
  - [ ] Defaults/templates updated to remove the retired instruction

Adhering to this lifecycle keeps instructions convergent, reduces conflicting guidance, and preserves the historical narrative needed for audits and future recursions.
