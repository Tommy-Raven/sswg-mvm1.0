---
anchor:
  anchor_id: docs_schema_tracking
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# Schema Tracking & Version Control — Updated

## Purpose

Maintains consistency of workflow templates and JSON outputs across system updates, ensuring backward and forward compatibility.

---

## Core Modules

* `ai_validation/schema_tracker.py` — Monitors schema usage, detects deviations, and validates workflow structure.
* `ai_validation/version_migrator.py` — Handles automatic upgrades, migration, and version reconciliation.

---

## Schema Fields

```yaml
schema:
  version: 1.0
  last_migration: "2025-11-03"
  compatible_versions: [0.9, 1.0]
  required_fields:
    - id
    - name
    - steps
    - phase_metadata
```

---

## Automatic Migration Example

```python
from ai_validation.version_migrator import SchemaMigrator

# Upgrade a workflow JSON to the latest schema version
SchemaMigrator().upgrade_schema("workflow_001.json")
```

---

## Notes

* Each schema change is logged with timestamp and migration notes.
* Compatibility checks prevent workflows from failing in older system versions.
* Supports integration with `ai_memory` to version and archive migrated workflows.
