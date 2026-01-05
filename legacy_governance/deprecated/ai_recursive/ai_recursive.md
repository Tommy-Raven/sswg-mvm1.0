> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

---
anchor:
  anchor_id: ai_recursive_ai_recursive
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# ai_recursive — Recursive Refinement Layer (SSWG MVM)

The `ai_recursive` package is responsible for **iterative improvement** of
workflows:

- Generate multiple candidate variants.
- Compare them against the current version and each other.
- Merge the best ideas into a new child workflow.
- Record version lineage for future analysis.

At the MVM stage, recursion is intentionally conservative and transparent.
Terminology aligns with `TERMINOLOGY.md` and outputs remain non_operational_output.

---

## Components

### 1. `variant_generator.py`

**Role:** Create alternative workflow variants from a base workflow.

MVM behavior:

- Accepts a workflow dict and a `num_variants` parameter.
- Returns a list of shallowly modified copies (e.g. different titles,
  small changes to metadata or module descriptions).
- Stubbed to be deterministic and safe; real generative logic can be
  plugged in later.

---

### 2. `version_diff_engine.py`

**Role:** Compare two workflow versions.

Responsibilities:

- Compute a structured diff between:
  - metadata
  - phases
  - modules
- Return a dict describing added/removed/changed elements.

Supports higher-level tools (history, version control, merge engine).

---

### 3. `merge_engine.py`

**Role:** Merge multiple variants into a single improved workflow.

MVM behavior:

- Start from a base workflow.
- For each variant:
  - merge metadata additions (non-conflicting keys)
  - prefer “longer” descriptions where appropriate
- Output a new workflow dict that preserves `workflow_id` and updates
  version/metadata explicitly.

Real-world merging logic can become more sophisticated over time.

---

### 4. `memory_adapter.py`

**Role:** Connect recursion with memory/history.

Responsibilities:

- Provide helpers to:
  - store variants in a memory store
  - retrieve previous versions
  - look up “best known” versions by id

At MVM, this is a thin wrapper that talks to `ai_memory` or
`generator/history` without creating a hard dependency tangle.

---

### 5. `version_control.py`

**Role:** Manage version naming and lineage.

Responsibilities:

- Provide `VersionController` with:
  - `next_child_version(parent_version)` helper
- Provide a convenience function:
  - `create_child_version(parent_workflow, child_body)` which:
    - assigns a new version string
    - records parent/child in history
    - returns the new workflow dict

This ties into `generator/history.py` for persistent lineage.

---

### 6. `recursion_manager.py`

**Role:** Enforce runtime guardrails for recursive refinement.

Responsibilities:

- Track depth, child counts, and cost budgets per recursion root.
- Require explicit termination conditions for every recursive call.
- Trigger external checkpoints as limits approach and halt on denial.
- Emit immutable audit snapshots (depth, parent id, budget remaining,
  termination condition, timestamp) for post-mortems.

Use `RecursionManager.prepare_call(...)` before spawning new children to
receive a `RecursionSnapshot` and ensure hard-stop enforcement.

---

## MVM Philosophy for Recursion

- **Safety first:** recursion should not infinitely loop or mutate in
  unpredictable ways at this stage.
- **Transparency:** each new version should be traceable back to its
  parent and diff-able.
- **Pluggability:** actual generative “brain” can be swapped in later
  (LLMs, heuristic rules, etc.), but the infrastructure remains stable.

## Formal Safety Constraints

To prevent runaway recursion, enforce the following guardrails at every
call site and within `recursion_manager.py`:

- **Depth ceilings:** hard-stop after a fixed recursion depth (e.g.,
  `max_depth=3`) or total generated children per root. Attempting to
  exceed the ceiling must raise a blocking error, not a warning.
- **Cost/complexity budgets:** track cumulative token/compute cost per
  recursion tree and halt once a configured budget is exhausted. Apply a
  complexity penalty (score decay) to each additional depth level to
  discourage overexpansion when selecting variants to keep.
- **External checkpoints:** require explicit approval from an external
  controller (human or orchestration layer) before spawning a new
  generation when thresholds are approached (e.g., within 80% of depth
  or cost limits). Checkpoints must log the current lineage snapshot and
  receive an explicit "continue" signal.
- **Termination proofs:** every recursive call must register a
  termination condition (depth reached, cost ceiling, or quality
  plateau) before execution. Calls lacking a verifiable termination
  criterion are rejected.
- **Audit trails:** record per-call metadata (depth, parent id, budget
  remaining, chosen termination condition). Logs must be immutable for
  the recursion window to enable post-mortem analysis and rollback.
