---
anchor:
  anchor_id: formal_guarantees_docs
  anchor_version: "1.0.0"
  scope: docs
  owner: docs
  status: draft
---

# Formal guarantees

## Scope

This document records the formal guarantees (or lack thereof) for recursion
termination and convergence in the sswg mvm runtime. The recursion policy is
summarized in the root [README](../README.md) and expanded in the architecture
notes in [docs/architecture/recursion_engine.md](./architecture/recursion_engine.md).

## Termination and convergence

**Convergence is not formally proven.** The current recursion engine only
commits to **heuristic termination** based on evaluation metrics and policy
thresholds. The system does not provide a mathematical convergence proof for
iterative refinement across all workflows, templates, or evaluation regimes.

Instead, termination is guaranteed by enforced guardrails and explicit policy
limits. These guardrails are implemented in
[`ai_recursive/recursion_manager.py`](../ai_recursive/recursion_manager.py) and
must be treated as the formal assumptions for bounded recursion:

- **Mandatory termination condition:** recursive calls require a
  `termination_condition`, otherwise the call raises a termination error.
- **Hard ceilings:** `max_depth` and `max_children` enforce bounded recursion.
- **Cost budgeting:** `cost_budget` caps cumulative cost for a recursion root.
- **Checkpoint gating:** `checkpoint_ratio` allows checkpoints to halt progress
  before limits are exceeded.
- **Audit trail:** each recursion call records immutable metadata required for
  provenance and replay.

## Formal assumptions linked to guardrails

The following assumptions are required for the heuristic termination guarantee:

1. **Guardrails are enabled** for any recursion call site that opts into
   `ai_recursive.RecursionManager`.
2. **Policy limits are finite** (`max_depth`, `max_children`, `cost_budget`) and
   enforced without overrides that remove bounds.
3. **Termination conditions are declared** at the call site and kept in the
   structured audit trail.

These assumptions map directly to the guardrails in
[`ai_recursive/recursion_manager.py`](../ai_recursive/recursion_manager.py) and
should be validated during recursion policy reviews.
