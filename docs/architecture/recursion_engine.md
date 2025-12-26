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

---

## ✅ Remediation 14 — Standardize Recursion-Trigger Conditions (Expanded)

### Why this remediation matters

A recursive system’s greatest danger is not that it can’t change—it’s that it can’t stop changing. Without standardized trigger conditions, recursion becomes impulsive: the system rewrites itself because it can, not because it should. That creates instability, drift, and needless complexity. Standardized recursion triggers turn recursion into a disciplined intervention: only fire when there is evidence of error, opportunity, or unmet objectives, and only at an appropriate scope and intensity.

Think of triggers as the system’s “governor” and “diagnostic thresholds,” not a creative whim generator.

---

### A. Failure Modes if Ignored (Expanded)

#### 1) Compulsive iteration and creative churn

**What this looks like**

- The system repeatedly rewrites artifacts even when they already meet objectives.
- Outputs oscillate: version A improves clarity, version B improves brevity, version C undoes both.
- Minor stylistic differences are treated as reasons to regenerate major structure.

**Why it happens**

- No stop condition or convergence criterion.
- No distinction between “nice-to-have” improvements and “must-fix” faults.
- No cost/benefit logic applied to recursion.

**What it breaks**

- Stability and trust.
- Maintainability: changes pile up faster than they can be evaluated.

---

#### 2) Wrong-level rewriting (scope mismatch)

**What this looks like**

- A localized defect triggers a global rewrite.
- The system changes module ordering when only one task was unclear.
- It expands depth when the real issue is missing prerequisites.

**Why it happens**

- Triggers aren’t linked to a “change radius” (how wide the edit should be).
- No diagnosis step to localize fault origin.

**What it breaks**

- Efficiency: wasted effort.
- Fidelity: unintended regressions increase with edit size.

---

#### 3) Drift disguised as “improvement”

**What this looks like**

- Repeated refinements slowly shift intent away from original user goals.
- Definitions mutate across iterations as the system “simplifies” them.
- The system begins optimizing for its own internal preferences.

**Why it happens**

- No anchor conditions tied to original intent.
- Triggers fire on superficial signals (e.g., “can be improved”) rather than target metrics.

**What it breaks**

- Intent alignment and correctness.
- Governance: you lose a stable canonical baseline.

---

#### 4) Trigger spam from noisy signals

**What this looks like**

- Small metric fluctuations cause rewrites even when changes are within expected variance.
- Agents disagree slightly, and the system treats disagreement as failure.
- The system becomes reactive rather than reflective.

**Why it happens**

- No tolerance bands or statistical smoothing.
- No differentiation between noise and true regression.
- No “cooldown” periods.

**What it breaks**

- Predictability and efficiency.
- Resource usage (compute, time, human review load).

---

### B. What “Good” Looks Like (Expanded)

#### 1) Triggers are typed: different triggers produce different kinds of recursion

Good systems separate triggers by category so the response matches the cause.

**Core trigger types**

- Error correction: contradictions, missing prerequisites, failed validation.
- Performance improvement: metrics below target; identifiable weak points.
- Coverage expansion: missing required components; domain growth request.
- Adaptation: new learner profile, new constraints, new environment.
- Maintenance: deprecated resources, drift detection, outdated assumptions.

**Outcome**

The system stops treating all problems as “rewrite everything.” Recursion becomes targeted: fix, improve, expand, adapt, maintain.

---

#### 2) Triggers include thresholds and tolerance bands

Trigger conditions should be measurable and robust to noise.

**What “good” means**

Each trigger has:

- signal definition (what is measured)
- threshold (when it fires)
- tolerance band (noise range)
- persistence rule (must persist across N evaluations)
- severity mapping (minor/major/critical)

**Outcome**

The system doesn’t thrash on minor fluctuations. Recursion fires when there is consistent evidence, not a single bad sample.

---

#### 3) Triggers are coupled to scope and intensity (“change radius”)

A key maturity feature: the system chooses how much to rewrite based on trigger severity.

**What “good” means**

- Small defects → local edits (task-level rewrite).
- Moderate issues → module rework (insert bridging content, reorder prerequisites).
- Critical failures → structural revision (rebuild dependency graph, revise core constraints).

**Outcome**

Changes are proportional. Risk of collateral damage drops.

---

#### 4) Explicit convergence and stop conditions

You need a definition of “good enough” to stabilize.

**What “good” means**

Convergence criteria such as:

- metrics meet thresholds
- no critical issues detected
- improvements plateau across multiple iterations

Stop rules:

- max recursion depth
- max attempts per defect
- escalation to human review when stagnation occurs

**Outcome**

The system can reach stable “canonical” states. Humans don’t get buried in endless micro-iterations.

---

#### 5) Triggers preserve intent through anchoring and invariants

Triggers must not allow the system to “improve itself” into a different system.

**What “good” means**

The system carries forward:

- original goals
- key constraints
- declared invariants

Trigger-driven edits must demonstrate that these anchors are preserved—or explicitly justify why not.

**Outcome**

Recursion remains aligned to user intent and governance constraints.

---

### C. Designing Triggers as a Policy Layer (Conceptual Framing)

A useful mental model: recursion triggers are a policy layer that decides:

1. Should we change anything? (trigger firing)
2. What kind of change is appropriate? (trigger type)
3. How big should the change be? (scope/intensity)
4. How do we verify improvement? (tie to evaluation checkpoints)
5. When do we stop and escalate? (convergence + human review)

This policy layer prevents “generator impulses” from masquerading as system evolution.

---

### D. Practical Examples (Conceptual)

**Example 1: Error correction trigger**

- Signal: contradiction count > 0
- Severity: critical if contradiction involves constraints; minor if stylistic
- Change radius: local fix for minor; structural fix for critical
- Persistence: immediate fire for critical; require N repeats for minor

**Example 2: Performance improvement trigger**

- Signal: clarity score below threshold and persists across two evaluations
- Change radius: task-level rewrite in the lowest-scoring module
- Stop: if clarity improves without regressions, promote; else branch

**Example 3: Drift trigger**

- Signal: divergence from canonical glossary increases over iterations
- Change radius: re-anchor definitions; re-run consistency checks
- Escalate: if drift persists after 2 cycles, require review

---

### E. Evaluation of trigger quality (how to know triggers are well-designed)

A trigger system is good if it passes these tests:

- **Stability test:** triggers do not fire repeatedly under normal variance.
- **Sensitivity test:** triggers fire reliably when genuine regressions occur.
- **Localization test:** triggered edits are appropriately scoped (no global rewrite for local defect).
- **Alignment test:** after trigger-driven changes, intent anchors remain intact.
- **Efficiency test:** improvements per iteration increase; wasted iterations decrease.

---

### Minimum viable model (MVM) — the mental model

The Minimum viable model (MVM) for recursion-trigger standardization is:

1. Three trigger categories to start: error correction, performance shortfall, drift.
2. Thresholds + persistence: each trigger fires only when evidence exceeds threshold and persists across N checks (except critical errors).
3. Change radius mapping: every trigger category maps to a default scope (task/module/structure).
4. Stop conditions: max iterations per defect + plateau detection + escalation rule.

This MVM prevents thrash and makes recursion purposeful immediately.

---

### mvm — the software posture (how it should behave)

As mvm (software), the system should:

- evaluate triggers before initiating recursion,
- classify trigger type and severity,
- choose proportional edit scope automatically,
- require evaluation checkpoints after changes,
- block promotion when triggers fired but evidence of improvement is absent,
- escalate to human review when triggers persist or plateau is detected.
