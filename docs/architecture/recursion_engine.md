sswg-mvm; version 1.0+ (living document)
Date: 05-03-2025
Document title: Recursion Engine (MVM Refinement)
Author: Tommy Raven
Licensing: Raven Recordings ©️ see: *LICENSE.md*
(Document) Purpose: Explain how the SSWG-focused recursion engine refines initial outputs, enforces schema alignment, and routes evaluation signals into new iterations. Provide architectural context tied to the root [README](../../README.md) and [docs/README.md](../README.md), noting where recursion integrates with memory, graph, and export layers.

# 🔁 Recursion Engine (MVM Refinement)

The recursion subsystem turns a first-pass workflow into a clearer, schema-aligned plan. It sits between generation and export, using metadata, dependency graphs, and evaluation scores to decide what to rewrite or expand. For a repository-level overview, see the top-level [README](../../README.md) and the documentation entrypoint at [docs/README.md](../README.md).

Key goals:

- analyze workflow structure for missing or malformed pieces
- rewrite inconsistent phases and low-signal steps
- suggest expansions when a template is too thin
- unify metadata and naming across artifacts
- adjust dependencies to keep the DAG consistent

This behavior is implemented primarily in [`generator/recursion_manager.py`](../../generator/recursion_manager.py) with supporting schemas and evaluation modules referenced in [docs/ARCHITECTURE.md](../ARCHITECTURE.md) and [docs/RECURSION_MANAGER.md](../RECURSION_MANAGER.md).

---

## 🧠 How Recursion Works (Abstract)

Each refinement pass applies layered checks:

1. **Structural audit**
   - detect missing fields and duplicate IDs
   - align phase ordering against schema expectations
   - cross-check dependencies against DAG construction (see [`ai_graph`](../../ai_graph/))

2. **Semantic strengthening**
   - expand vague phases into clear task verbs
   - align tone and detail with repository docs (e.g., [docs/SEMANTIC_ANALYSIS.md](../SEMANTIC_ANALYSIS.md))
   - normalize clarity and density based on evaluation scores

3. **Dependency tightening**
   - insert implied prerequisites when edges are missing
   - remove cycles flagged by the graph validator
   - ensure downstream phases refer only to produced outputs

4. **Metadata normalization**
   - canonical phase and task naming
   - version format enforcement per [`schemas/workflow_schema.json`](../../schemas/workflow_schema.json)
   - consistent provenance fields for lineage tracking

5. **Evaluation-based adjustments**
   - if clarity or density drops below thresholds, regenerate the affected phase
   - record deltas in the memory subsystem (`ai_memory`) for lineage (see [docs/EVOLUTION_LOGGING.md](../EVOLUTION_LOGGING.md))

---

## 🧱 Hardening the Recursion Engine

Clear guardrails keep iterative passes aligned with their original intent and rationale.

**Failure mode if ignored:**

- outputs diverge in style, tone, or intent over iterations
- later generations contradict earlier assumptions
- the system loses track of why a decision was made

**What good looks like:**

- each generation explicitly references prior rationale and logged decisions
- recursion operates through deltas, not full rewrites, so the lineage stays transparent
- the system can explain what changed and why across iterations, backed by structured logs

Operationally, this means every recursion call should pull the last saved delta from `ai_memory`, annotate adjustments in the structured logger, and pass both into evaluators to confirm intent alignment before proceeding.

---

## 🧭 Normalize and Harden Schema Logic

Schema rigor prevents ambiguity as recursive refinements accumulate.

**Why it matters:** Creative systems still require structure; without schema rigor, expressive freedom becomes ambiguity.

**Failure mode if ignored:**

- inconsistent field meanings between iterations or templates
- partial or malformed artifacts that block downstream validators
- consumers misinterpret intent because optional vs. required elements are unclear

**What good looks like:**

- every field maps to a single semantic meaning and is reused consistently
- optional vs. required elements are explicit in both schemas and prompts
- schema changes are versioned, backward-aware, and logged so recursion can reconcile old and new shapes

In practice, tie each recursion pass to the authoritative JSON schemas in `schemas/`, require version tags in emitted metadata, and surface schema diffs in telemetry to guard downstream consumers.

---

## 🔁 Recursion Depth and Control

The current MVM ships a minimal entry point:

```python
simple_refiner(workflow)
```

Depth is intentionally bounded to keep refinements deterministic. Future iterations may introduce:

- configurable N-depth recursion with guardrails from [`config/`](../../config)
- tree-branching or alternative templates when convergence stalls
- cross-template hybridization coordinated through the plugin guides in [docs/PLUGIN_DEVELOPMENT.md](../PLUGIN_DEVELOPMENT.md)

Governance notes and architectural placement are summarized in [docs/ARCHITECTURE.md](../ARCHITECTURE.md) and the system overview in [docs/architecture/system_architecture.md](./system_architecture.md).

---

## 🧪 Regeneration Triggers and Logging

Common triggers for a refinement cycle include:

- large diff size between generated and validated graphs
- low `clarity_score` or evaluation metrics
- missing dependency links detected during validation
- schema failures that can be auto-corrected by the recursive pass

Every recursion run emits a structured log event:

```
mvm.process.refined
```

These events feed into the monitoring pipeline described in [docs/TELEMETRY_GUIDE.md](../TELEMETRY_GUIDE.md) and align with the logging posture highlighted in the root [README](../../README.md).
