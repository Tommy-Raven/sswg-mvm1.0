> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

---
anchor:
  anchor_id: generator_generator
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# generator/ — SSWG Workflow Generator (MVM Layer)

The `generator` package orchestrates a single end-to-end generation run:

1. Parse user configuration (purpose, audience, style, etc.).
2. Build a workflow ID and base metadata.
3. Run the core phases via `ai_conductor.Workflow`.
4. Optionally invoke recursive expansion (via `ai_recursive` / `RecursionManager`).
5. Evaluate, score, and export artifacts (JSON + Markdown).
6. Persist outputs via `ai_memory.MemoryStore` and log telemetry.

At the **MVM stage**, the goal is:

- deterministic, debuggable behavior,
- clear separation of concerns,
- extension hooks for recursion, plugins, and richer scoring.

Core utilities are centralized for deterministic behavior:

- Audit hashing and timestamps in `ai_cores/audit_core.py`
- Export serialization in `ai_cores/export_core.py`
- Module registry storage in `ai_cores/module_core.py`

Terminology aligns with `TERMINOLOGY.md` and outputs remain non_operational_output.

## Key Modules

- `async_executor.py` — run async tasks and fan-out workloads.
- `cache_manager.py` — async cache for serialized artifacts.
- `config.py` — async-aware configuration manager.
- `evaluation.py` — phase-level evaluation orchestration.
- `exception_handler.py` — sync/async exception wrappers.
- `exporters.py` — JSON/Markdown export helpers.
- `history.py` — high-level history/lineage hooks.
- `modules.py` — generator-specific module registry.
- `performance_tracker.py` — timing and performance summaries.
- `plugin_loader.py` — dynamic loader for generator plugins.
- `recursive_expansion.py` — integration glue for recursive generation.
- `semantic_scorer.py` — semantic/quality scoring helpers.
- `utils.py` — workflow IDs and basic logging.
- `workflow.py` — phase-specific helpers (`run_phase_1`…`run_phase_5`).
