# ai_validation — Validation Layer for SSWG MVM

The `ai_validation` package provides the core validation and safety checks
for SSWG workflows and related artifacts. At the MVM (Minimum Viable Model)
stage, the focus is on **schema correctness**, **regression guardrails**, and
**safe evolution of versions**.

---

## Components

### 1. `schema_validator.py`

**Role:** Canonical JSON Schema validation entrypoint.

Provides:

- `validate_workflow(workflow_obj, schema_name="workflow_schema.json")`  
  Validates a workflow dict against the main workflow schema in `schemas/`.

- `validate_json(obj, schema_name=None)`  
  Generic JSON validation helper.  
  - If `schema_name` is `None`, acts as a no-op that returns `True`.  
  - If a schema name is provided and found, logs all schema errors and returns
    `False` on failure.

This module is intentionally tolerant in the MVM phase: missing schemas or
validation failures do **not** hard-crash the system but emit warnings and
telemetry instead.

---

### 2. `schema_tracker.py` (planned / MVM stub)

**Goal:** Track which schemas are used where, and how they evolve over time.

Responsibilities (design intent):

- Maintain a registry of known schema files in `schemas/`.
- Provide utilities to:
  - List all available schemas.
  - Check which schema version was used for a given workflow artifact.
  - Emit telemetry when schema versions change.

At the MVM stage, this can be implemented as:

- A thin wrapper that:
  - Enumerates files in `schemas/`.
  - Provides simple helpers like `get_schema_path(name)`.

---

### 3. `regression_tests.py` (planned / MVM stub)

**Goal:** Provide quick regression checks for core workflows.

Intended responsibilities:

- Load a small suite of canonical test workflows (e.g. from `tests/resources/`).
- Validate them with `validate_workflow`.
- Optionally run them through the generator pipeline and assert:
  - Schema validity.
  - Presence of required fields.
  - Absence of dependency cycles.

For MVM, this can be a simple CLI or pytest-compatible module that:

- Runs `validate_workflow` on a set of JSONs.
- Prints a summary of pass/fail results.

---

### 4. `version_migrator.py` (planned / MVM stub)

**Goal:** Safely migrate workflow artifacts between schema versions.

Intended responsibilities:

- Define small, explicit migration functions, e.g.:
  - `migrate_1_0_to_1_1(workflow: dict) -> dict`
  - `migrate_1_1_to_2_0(workflow: dict) -> dict`
- Orchestrate migration chains:
  - `migrate_to_latest(workflow: dict, from_version: str) -> dict`

In the MVM, it is acceptable to:

- Implement only no-op migrations (copy + tag with new version).
- Focus on a well-documented pattern for future real migrations.

---

## MVM Philosophy for Validation

- **Warn, don’t brick:** validation should surface issues loudly, but not
  crash the pipeline at this stage.
- **Schema-first:** workflows should be describable and checkable via JSON
  schemas; the code is a thin layer around that.
- **Composable:** validators should be easy to plug into:
  - generator
  - recursion manager
  - exporters
  - history/evolution tracking

This file should be updated as the validation layer evolves beyond MVM.
