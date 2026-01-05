> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

---
anchor:
  anchor_id: docs_architecture_recursion_engine
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

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
The recursion policy (guardrails and termination semantics) is summarized in the root [README](../../README.md), with formal guarantees and assumptions in [docs/FORMAL_GUARANTEES.md](../FORMAL_GUARANTEES.md).

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

---

## ✅ Remediation 15 — Enhance Error-Handling and Recovery Protocols (Expanded)

### Why this remediation matters

A recursive system will inevitably produce failures: malformed artifacts, contradictory outputs, missing prerequisites, incompatible merges, or “improvements” that actually regress quality. The difference between a fragile recursive generator and a durable evolving system is whether it can detect failure early, isolate damage, recover cleanly, and learn from the incident without corrupting its own lineage.

Error-handling is not merely catching exceptions; it is governance for failure. Recovery protocols are what keep iterative evolution from turning into iterative decay.

---

### A. Failure Modes if Ignored (Expanded)

#### 1) Silent corruption of the knowledge lineage

**What this looks like**

- A flawed iteration is promoted because it “looks fine,” then becomes the new baseline.
- Future iterations inherit contradictions or missing constraints.
- Errors compound across generations until the system becomes incoherent.

**Why it happens**

- No robust validation gates.
- Errors are detected late (or not at all).
- No quarantine state for suspicious outputs.

**What it breaks**

- Trust and auditability.
- Long-term coherence of the domain knowledge base.

---

#### 2) Cascading failures across dependent artifacts

**What this looks like**

- One broken definition causes many tasks/modules to become inconsistent.
- Fix attempts introduce more breakage because dependencies weren’t considered during recovery.
- A small defect becomes a system-wide incident.

**Why it happens**

- No dependency-aware impact analysis during recovery.
- No staged rollback: changes are applied broadly and quickly.

**What it breaks**

- Maintainability and performance.
- The ability to iterate safely at scale.

---

#### 3) Overcorrection and thrash

**What this looks like**

- The system responds to a local error with a global rewrite.
- Multiple recovery attempts oscillate without converging.
- The system “fights itself”: fixes undo prior fixes.

**Why it happens**

- No root-cause diagnosis step.
- No bounded recovery actions tied to error type and severity.
- No “cooldown” or escalation threshold after repeated failures.

**What it breaks**

- Efficiency and stability.
- Confidence in promotion decisions.

---

#### 4) Human escalation overload

**What this looks like**

- Every small issue asks for human review.
- Humans become the error handler, not the system.
- The system never develops autonomy because it never learns to self-recover.

**Why it happens**

- No severity model distinguishing blockers from nuisances.
- No automatic remediation pathways for common faults.

**What it breaks**

- Operational viability.
- Scalability and adoption.

---

### B. What “Good” Looks Like (Expanded)

#### 1) Early detection with explicit error taxonomy

The system should recognize and label failures as specific classes, not generic “something went wrong.”

**Common error classes**

- Structural: malformed format, missing required fields, invalid ordering.
- Semantic: contradictions, term collisions, missing prerequisites.
- Behavioral: poor evaluation outcomes, low usability, high intervention.
- Safety/compliance: policy violations, privacy risks, disallowed content.
- Operational: resource missing, dependency mismatch, incompatible versions.

**Outcome**

Recovery becomes targeted and reliable instead of guesswork.

---

#### 2) Quarantine and containment: unsafe outputs never become baseline

A mature system treats suspicious iterations as quarantined until proven safe.

**What “good” means**

- New outputs enter a sandbox/quarantine state by default.
- Promotion requires passing validation + evaluation gates.
- Any safety/compliance flags trigger mandatory review or auto-rejection.

**Outcome**

The lineage remains clean. Failures become experiments, not infections.

---

#### 3) Root-cause analysis before remediation

Good recovery starts with diagnosis, not reaction.

**What “good” means**

The system attempts to localize:

- where the fault originates (module/task/definition/constraint)
- what dependencies are implicated
- which change introduced it (diff-aware)

It distinguishes symptoms from causes (e.g., “users fail step 5” may be caused by missing prerequisite in step 2).

**Outcome**

Fixes become smaller, safer, and faster. Repeated error loops diminish over time.

---

#### 4) Bounded recovery playbooks per error type

For each error class, the system has a preferred recovery strategy.

**What “good” means**

- Structural errors: repair formatting/required fields; revalidate.
- Semantic errors: resolve contradictions by re-anchoring definitions; rerun coherence checks.
- Behavioral regressions: rollback to last stable; branch an experimental variant for further work.
- Safety flags: immediate quarantine; strip/replace risky segments; escalate if unclear.
- Operational errors: degrade gracefully (fallback resources, alternate tasks) or fail fast with clear diagnostics.

**Outcome**

Recovery is predictable and auditable. Humans intervene only when the system genuinely cannot resolve ambiguity.

---

#### 5) Rollback is first-class and fast

Recovery requires the ability to revert cleanly.

**What “good” means**

- Every iteration is versioned and reversible.
- The system can revert to last known-good on threshold violations.
- The failed version is preserved as an artifact for analysis, not deleted.

**Outcome**

The system can experiment aggressively without risking permanent degradation.

---

#### 6) Learning from failures: incident-to-improvement loop

Failures should update system behavior so they recur less often.

**What “good” means**

Each failure produces:

- a short incident record (what happened, where, severity)
- root-cause hypothesis
- applied fix
- prevention rule (new validation check, new trigger threshold, new constraint)

Frequent failures create “guardrails” automatically (or propose them for review).

**Outcome**

Over time, the system’s failure rate drops and its autonomy rises.

---

### C. Practical Framing: A Recovery Protocol as a Controlled Sequence

Error-handling works best when it is staged and repeatable.

A clean mental model is:

1. Detect (identify error signals)
2. Classify (assign error taxonomy class + severity)
3. Contain (quarantine; prevent promotion)
4. Diagnose (root cause localization + dependency impact)
5. Remediate (bounded fix playbook)
6. Re-validate (structural + semantic checks)
7. Re-evaluate (quality metrics + regression guards)
8. Decide (promote, rollback, branch, or escalate)
9. Record (incident log + prevention update)

This prevents chaotic, ad hoc “fixing.”

---

### D. Severity Model (the missing spine in most systems)

Recovery protocols need severity tiers to avoid over-escalation.

**Typical tiers**

- Critical: safety/compliance violation, core contradictions, corrupted schema → immediate quarantine + rollback.
- Major: significant regression in key metrics, broken prerequisites → rollback or targeted fix, re-evaluate.
- Minor: stylistic issues, small clarity dips within tolerance → adjust next iteration; no rollback needed.
- Informational: warnings, non-blocking inconsistencies → log and monitor.

Good systems treat severity as a routing mechanism: it determines whether to fix locally, rollback, branch, or escalate.

---

### E. Concrete Examples (Conceptual)

**Example 1: Semantic contradiction appears after refinement**

- Detection: contradiction signal > threshold
- Containment: quarantine version
- Diagnosis: identify conflicting definitions introduced in last diff
- Remediation: re-anchor to canonical glossary; update dependent tasks
- Re-validation: contradiction count returns to zero
- Decision: promote if metrics stable; else branch

**Example 2: Evaluation regression despite structural validity**

- Detection: clarity score drops below guard
- Containment: block promotion
- Diagnosis: locate tasks with highest failure rate
- Remediation: revert that task to prior stable variant; keep experimental rewrite in branch
- Decision: mainline remains stable; branch continues iteration

**Example 3: Resource missing / operational failure**

- Detection: resource resolution fails
- Remediation: degrade gracefully to alternate resource or generated substitute
- If substitution affects quality: mark as “provisional,” require review before promotion

---

### Minimum viable model (MVM) — the mental model

The Minimum viable model (MVM) for error-handling and recovery protocols is:

1. Error taxonomy + severity tiers (structural/semantic/behavioral/safety/operational + critical/major/minor).
2. Quarantine by default for new iterations; promotion requires passing gates.
3. Rollback to last known-good for critical/major regressions.
4. Bounded playbooks: one preferred recovery action per error class.
5. Incident record stored with the version: what failed, why, what was done.

This MVM makes the system durable immediately without heavy overhead.

---

### mvm — the software posture (how it should behave)

As mvm (software), the system should:

- treat every generated artifact as untrusted until validated,
- classify errors and route recovery automatically,
- quarantine unsafe iterations,
- rollback rapidly on regression guards,
- preserve failed variants for learning,
- update prevention checks based on repeated incidents,
- escalate to humans only when severity is high or ambiguity is irreducible.

---

## 🧪 Entropy Stop Condition (v1.2.0)

Bounded cognition introduces an entropy-governed termination rule. Recursion halts when additional refinement increases entropy faster than verity gains:

```
Stop when: ∂V/∂E ≤ 0
```

Where:
- **V** = verity (semantic × deterministic × entropic alignment)
- **E** = entropy cost per recursion step

**Operational rule:** when the verity gradient no longer exceeds entropy cost, the recursion manager exits and records the termination state in telemetry.
