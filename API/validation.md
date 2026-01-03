---
anchor:
  anchor_id: api_validation
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# ✔ Validation API (ai_validation/)  
### JSON Schema Enforcement & Regression Tests

---

# 🧠 Schema Validator

## `validate_workflow(workflow) -> (bool, str)`
Runs the full JSON schema check.

- Ensures required fields exist  
- Validates structure of phases + tasks  
- Enforces dependency graph format  
- Rejects foreign keys or unknown fields  

### Example:
```python
valid, err = validate_workflow(wf)
```

---

# 📚 Schema Tracker

Tracks which schema version is active.

---

# 🔁 Version Migrator

## `migrate(workflow, target_version)`
For upgrading workflow formats across schema updates.

(Framework stub for v1.0)

---

# 🧪 Regression Tests

Automated checks to ensure:

- schema stability  
- structural invariants  
- backward compatibility
