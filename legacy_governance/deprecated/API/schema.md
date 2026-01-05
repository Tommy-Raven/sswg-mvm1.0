> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

---
anchor:
  anchor_id: api_schema
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

---

## **docs/api/schemas.md**
```markdown
# 📐 Workflow Schema API

SSWG–MVM is fully schema-driven.

Schemas define:

- Required fields  
- Structural constraints  
- Valid value types  
- Dependency requirements  
- Evaluation objects  
- Phase/task structure  

---

## 📄 Available Schemas

### `workflow_schema.json`  
The master schema used for validation.

### `phase_schema.json`  
Defines what a valid workflow phase must contain.

### `metadata_schema.json`  
Defines required metadata fields:
- purpose  
- audience  
- created  
- author  
- version  

### `dependency_schema.json`  
Defines valid DAG-style dependencies.

---

## 🔍 Schema API Functions

### `get_schema(name: str) -> dict`
Returns a schema as a Python dictionary.

### `validate_json(data: dict, schema: dict) -> tuple[bool, str]`
Raw validation entrypoint.

### `validate_workflow(wf: dict) -> tuple[bool, str]`
Full workflow validator.

---

## 🧪 Example: Validate a Workflow

```python
from ai_validation.schema_validator import validate_workflow

valid, error = validate_workflow(workflow_dict)

if valid:
    print("Workflow is valid!")
else:
    print("Error:", error)
