---
anchor:
  anchor_id: api_recursion
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# 🔁 Recursion API (ai_recursive/)  
### Version Diff Engine · Variant Generator · Memory Adapter

MVM supports early-stage recursive refinement and lays the foundation for full regeneration cycles.

---

# 🔍 Version Diff Engine

## `compare_workflows(old_path, new_path)`
High-level diff comparison.

## `compute_diff_summary(wf_old, wf_new)`
Produces:

```json
{
  "changed_fields": [...],
  "added_phases": [...],
  "removed_phases": [...],
  "modified_phases": [...],
  "diff_size": 4,
  "regeneration_recommended": true
}
```

## `regenerate_if_needed()`
Triggers orchestration if diff is large enough.

---

# 🧪 Variant Generator (stub)

Will support:

- multi-branch mutation  
- random task perturbation  
- recombination of workflows  

---

# 🗂 Memory Adapter

In future:  
Bridge recursive cycles with long-term memory (semantic persistence).

---

# 🧠 Version Control

Minimal placeholder for lineage/version tracking.
