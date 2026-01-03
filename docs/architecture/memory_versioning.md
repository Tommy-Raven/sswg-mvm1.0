---
anchor:
  anchor_id: docs_architecture_memory_versioning
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

sswg-mvm; version 1.0+ (living document)
Date: 05-03-2025
Document title: Memory, Lineage & Versioning
Author: Tommy Raven
Licensing: Raven Recordings ©️ see: *LICENSE.md*
(Document) Purpose: Detail how the SSWG-MVM tracks workflow history, lineage, and regeneration triggers. Explain memory storage, schema alignment, and graph interactions so SSWG-focused iterations remain reproducible. Provide navigation anchors to the root [README](../../README.md) and [docs/README.md](../README.md).

# 🧬 Memory, Lineage & Versioning

SSWG-MVM includes a **long-term memory subsystem** that logs workflow evolution and triggers intelligent regeneration.

Modules:  
```
ai_memory/
```

---

# 📝 Components

### 1. FeedbackIntegrator  
Records:  
- diff summaries  
- clarity scores  
- regeneration triggers  
- historical averages  

### 2. MemoryStore  
Stores:  
```
data/workflows/<workflow_id>_<timestamp>.json
```

### 3. HistoryManager  
Tracks parent → child relationships.

---

# 🔢 Version Format

```
v.<major>.<minor>.mvm.<patch>
```

Example:

```
v.09.mvm.25
```

Automatically bumped by CI when core modules change.

---

# 🧩 Regeneration Model

Regeneration triggers when:

- diff_size is large  
- clarity_score < threshold  
- missing phases  
- dependency cycle not corrected  

---

# 🔍 Example History Entry

```json
{
  "parent_workflow": "workflow_a",
  "child_workflow": "workflow_b",
  "modifications": ["Module count changed"],
  "score_delta": 0.42,
  "metadata": {
    "original_eval": {...},
    "refined_eval": {...}
  }
}
```

---

# 🔮 Future Enhancements

- embedding-based semantic memory  
- grimoire pages (inter-template recollection)  
- plugin ecosystem for persistent domains

---

# 📡 Telemetry Storage Extensions (v1.2.0)

The memory subsystem now stores cognitive thermodynamic signals alongside lineage metadata.

**New telemetry storage types:**

- `entropy_log`
- `determinism_curve`
- `verity_curve`

These logs persist with workflow lineage snapshots, enabling audit-ready reproduction of bounded cognition decisions.

---

# 🧪 Benchmark Evolution Tracking

The module `ai_memory/benchmark_evolution.py` records verity and entropy trajectories across recursion runs. It provides the longitudinal record used to validate that bounded cognition converges without violating determinism.
