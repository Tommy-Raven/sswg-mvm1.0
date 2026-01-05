> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

---
anchor:
  anchor_id: docs_getting_started_run_mvm
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# Running SSWG-MVM

**Canonical runbook (how to run + expected outputs):** `docs/RUNBOOK.md` is the primary entrypoint. This document is secondary/overview and should defer to the canonical runbook to avoid drift.

## Generate a Workflow (default template)

```bash
python3 -m generator.main --preview
```

## Specify a Template

```bash
python3 -m generator.main --template technical
```

## Export Artifacts

Artifacts appear under:

```
data/outputs/
```

Includes:

- JSON  
- Markdown  
- Mermaid DAG  

---

# Run Without Refinement

```bash
python3 -m generator.main --no-refine
```

---

# Enable/Disable History Tracking

```bash
python3 -m generator.main --no-history
```

---

# Full Options

```bash
python3 -m generator.main --help
```

---

# 🧠 Entropy-Governed Recursion (v1.2.0)

Run bounded cognition with entropy governance enabled:

```bash
python -m generator.recursion_manager --bounded --entropy-budget 1.0
```

This mode halts recursion when verity gains no longer exceed entropy cost.
