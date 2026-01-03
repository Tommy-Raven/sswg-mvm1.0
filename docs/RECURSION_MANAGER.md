---
anchor:
  anchor_id: docs_recursion_manager
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# Recursion Manager

## Purpose

The **Recursion Manager** is the central controller for managing recursive workflow expansion, enforcing depth limits, stopping conditions, and cache utilization. It ensures that workflow iterations converge and prevents infinite loops.

---

## Responsibilities

* Track recursion depth, iteration counts, and phase progression.
* Prevent infinite recursion loops and redundant computation.
* Interface with `ai_evaluation.semantic_analysis` to detect content stability and convergence.
* Manage recursion parameters through configuration (`config/recursion.yml`) or programmatically.
* Coordinate caching, rollback, and version tracking with `ai_memory.store`.

---

## Example Configuration (`recursion.yml`)

```yaml
recursion:
  max_depth: 5
  min_delta_score: 0.15
  halt_on_no_improvement: true
  cache_reuse: true
```

---

## Example Usage

```python
from generator.recursion_manager import RecursionManager
from data.workflows import load_workflow

# Load base workflow
workflow = load_workflow("example_workflow.json")

# Initialize Recursion Manager
rm = RecursionManager(max_depth=5, min_delta_score=0.15)

# Run recursive cycle
rm.run_cycle(workflow)
```

---

## Notes

* The recursion manager leverages **semantic delta scoring** to determine whether a workflow has sufficiently stabilized.
* All iterations are logged to `ai_memory/` with versioned identifiers.
* Optional integration with FastAPI endpoints allows remote triggering of recursive cycles.
