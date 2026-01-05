> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

---
anchor:
  anchor_id: api_core
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# 🧬 Core API (ai_conductor/)
### Orchestrator, Phase Controller, Module Registry

---

# 🎛 Orchestrator

## `class Orchestrator:`
Central coordination engine for workflow creation and validation.

### Key Methods

#### `run(user_config, recursive=False)`
- Generates workflow
- Validates schema
- Saves workflow to memory
- (Optional) performs recursive expansions
- Triggers telemetry + dashboard updates

---

# 🧩 Phase Controller

## `class PhaseController`
Executes transformation phases in order.

### Responsibilities:
- manage input/output between phases
- track internal phase metadata
- unify phase schemas

### Canonical 9-Phase Model

The core pipeline is defined as the canonical 9-phase flow:

1. ingest
2. normalize
3. parse
4. analyze
5. generate
6. validate
7. compare
8. interpret
9. log

Each phase must use its declared handler and I/O contracts from `schemas/pdl-phases/`.

---

# 📦 Module Registry

## `class ModuleRegistry`
Provides module lookup and dependency tracking for workflow assembly.

Planned expansions include:
- plugin loading
- stricter module naming enforcement

---

# 📄 Workflow Object

## `class Workflow`
A lightweight container for:

```python
workflow_id: str
params: dict
results: dict
```

Primary method:

### `run_all_phases()`
Executes the canonical phase sequence for workflow execution.

---

# 🧪 Dev-Only Mock Behavior

Legacy compatibility mode remains available for development and testing:

- `Workflow.run_all_phases()` currently uses stubbed phase execution in `ai_conductor/workflow.py`.
- `Workflow.execute_phase()` returns stubbed payloads and should not be used for canonical runs.

Production runs should rely on the canonical PDL-driven execution and handler resolution defined in `pdl/handlers.py`.
