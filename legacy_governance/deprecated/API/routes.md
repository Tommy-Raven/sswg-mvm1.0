> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

---
anchor:
  anchor_id: api_routes
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# 🌍 SSWG–MVM API Routes  
**Canonical HTTP Interface for Workflow Generation, Validation & Recursion**

The SSWG–MVM engine exposes a clean, predictable, schema-aligned REST API designed for automation, tooling integration, and recursive meta-workflow pipelines.  
Every route returns structured JSON and follows deterministic behavior based on the MVM core.

---

# 🔌 Base URL  
By default (local development):

http://localhost:8000/api

Production-style deployments typically mount under the same `/api` root.

---

# 🚀 Workflow Lifecycle Endpoints

## **POST /api/workflows/generate**
> Generate a complete workflow from user-provided intent.

### **Request Body**

> {
  "purpose": "Design a robotics training curriculum",
  "audience": "Engineering students",
  "style": "Technical-formal",
  "language": "en-US"
}

### Response

> {
  "workflow_id": "wf_rob_001",
  "version": "v1.2.0",
  "metadata": { ... },
  "phases": [ ... ],
  "dependency_graph": { ... }
}


---

## POST /api/workflows/refine

-Apply recursive refinement via the Recursion Manager.

### Request Body

> {
  "workflow": { ... },
  "depth": 2
}

### Response

> {
  "workflow_id": "wf_rob_001_r2",
  "refinement_depth": 2,
  "phases": [ ...updated... ]
}


## POST /api/workflows/validate

—Validate any workflow dict against the official SSWG–MVM schema.

### Request Body

> {
  "workflow": { ... }
}

### Response

> {
  "valid": true,
  "errors": []
}

—If invalid:

> {
  "valid": false,
  "errors": [
    "metadata.purpose: required field missing",
    "phases[0].tasks: must be an array of objects"
  ]
}


## GET /api/workflows/export/{workflow_id}

—Export workflow artifacts produced by the generator.

### Returns a mapping of artifact types:

> {
  "workflow_id": "wf_example",
  "json": "data/outputs/wf_example.json",
  "markdown": "data/outputs/wf_example.md",
  "mermaid": "data/outputs/wf_example.mmd"
}

—If the workflow ID is unknown:

> {
  "error": "Workflow not found: wf_example"
}


---

# 📚 Schema Endpoints

## GET /api/schemas

—List all available schema files.

### Response

> {
  "schemas": [
    "workflow_schema.json",
    "phase_schema.json",
    "dependency_schema.json",
    "metadata_schema.json"
  ]
}


---

## GET /api/schemas/{name}

—Return a specific schema as JSON.

> Example:

> GET /api/schemas/workflow_schema.json

### Response

> {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": { ... }
}


# ⚙️ Utility Endpoints

## GET /api/status

—Quick health check of the engine.

### Response

> {
  "status": "ok",
  "engine": "SSWG–MVM",
  "version": "v1.2.0"
}

## GET /api/version

— Returns MVM version + recursion profile.

> {
  "version": "v1.2.0",
  "profile": "sswg_mvm_v0_1"
}


---

# 🧪 Testing Endpoints (Optional / Dev Mode Only)

## POST /api/debug/evaluate

—Run evaluation metrics directly.

> {
  "workflow": { ... }
}

### Response

> {
  "clarity_score": 0.87,
  "structure_score": 0.92,
  "coverage_score": 0.78
}

*Dev-mode routes are controlled via environment variables.*


---

# 🧭 Summary Table

| Method | Route                          | Purpose                           |
|--------|--------------------------------|-----------------------------------|
| POST   | /api/workflows/generate        | Create new workflow               |
| POST   | /api/workflows/refine          | Recursive refinement              |
| POST   | /api/workflows/validate        | Schema validation                 |
| GET    | /api/workflows/export/{id}     | Export artifacts                  |
| GET    | /api/schemas                   | List schemas                      |
| GET    | /api/schemas/{name}            | Retrieve specific schema          |
| GET    | /api/status                    | Health check                      |
| GET    | /api/version                   | Engine version info               |
| POST   | /api/debug/evaluate            | Metric evaluation (dev only)      |
