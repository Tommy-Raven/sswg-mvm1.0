Below is a fully rewritten, updated schema.md, aligned with:
* SSWG-MVM philosophy
* `ts/dtr` versioning logic
* the canonical repo structure
* deterministic + transitive semantic expectations
* local-relative `$ref` resolution
* strict naming conventions
* separation of canonical schemas vs. expandable metadata


---
 
# SSWG-MVM Schema Overview
### *(Updated & Standardized to Current SSWG-1.0.0mvm Specifications)*

> This directory defines the JSON Schemas used by the SSWG Minimum Viable Model (MVM) and all future `ts/dtr` builds. These schemas formalize the structure, semantics, and constraints of workflows, phases, tasks, recursion metadata, modules, ontology views, and evaluation systems. 
>> *Every schema in this directory is considered canonical and participates directly in SSWG’s deterministic + transitive semantic model. Once released, schemas are immutable under versioning rules (see SSWG-Versioning-Logic.md).*

---

# 1. General Schema Standards

All schemas:

+• Use JSON Schema Draft `2020-12`
• Declare a stable, canonical `$id` under the repository’s schemas/ directory
• Use relative `$ref` values that resolve locally via the validation layer
• Follow strict property governance (`additionalProperties: false` by default unless extensibility is intentional)
• Maintain filename = `$id` alignment
• Are versioned using SSWG’s ts-line (Transitive Semantic versioning)

Schemas collectively enforce deterministic output across all workflow-generation operations.

## 1.1 `$schema` declaration

All schemas begin with:

`https://json-schema.org/draft/2020-12/schema`

## 1.2 `$id` pattern

Example:

`https://github.com/Tommy-Raven/SSWG-mvm1.0/tree/main/schemas/workflow_schema.json`

Each `$id` serves as a globally unique identifier and version anchor, even though resolution is performed locally.

## 1.3 `$ref` pattern

Example:

{ `"$ref": "metadata_schema.json"` }

Relative `$ref` values must always be local sibling files within the schemas/ directory.
Local resolution is handled by:

ai_validation/schema_validator.py
`(base URI = SCHEMAS_DIR.as_uri())`


---

# 2. The Workflow Schema (Root Contract)

`workflow_schema.json`

Canonical definition of a complete SSWG workflow.

**Role**

Defines the highest-level structure all workflows must follow.
Ensures workflows remain deterministic, metadata-governed, and fully schema-validatable.

**Key Properties**

`Type: object`
> Required fields: `workflow_id`, `version`, `metadata`, `phases`

*Properties include:*
>
• `workflow_id` – string (^[a-zA-Z0-9_-]+$)
• `version` – string (ts/dtr tagging allowed)
• `metadata` – $ref → metadata_schema.json
• `phases` – array of phase_schema.json, minimum 1
• `modules` – array of module_schema.json
• `semantics` – array of semantics_schema.json
• `evaluation` – $ref → evaluation_schema.json
• `recursion` – $ref → recursion_schema.json
• `dependency_graph` – object with:
 > nodes: array of strings
 > edges: array of 2-element arrays [from, to]

### Strictness

`additionalProperties: false`
No undeclared fields are permitted.

Used by

• ai_validation/schema_validator.py
• generator/main.py
• `dependency-graph` builder
• future recursive refiners (ts/dtr line)

--- 


# 3. Structural Schemas (Core)


---

## 3.1 phase_schema.json

Defines a single workflow phase.

**Role**

Represents an atomic stage of processing inside a workflow (ingest, parse, generate, output, validate, log).

**Key Properties**

*Type: object*
Required: id, title, tasks

* id – string
* title – string
* description – optional string
* tasks – array of task_schema.json
* subphases – recursive array of phase_schema.json
* evaluation_schema – $ref to evaluation_schema.json

**Strictness:**  `additionalProperties = false`

*Referenced by: workflow_schema.json → phases[*]*


---

## 3.2 task_schema.json

Defines an atomic, instructional task.

**Role**

The smallest executable unit used by the assistant or engine.

**Key Properties**

*Type: object*
*Required: title*

* title – string
* instruction – string
* inputs – array of strings
* outputs – array of strings
* ai_task_logic – string
* dependencies – array of strings
* semantic_tag – string
* evaluation_hint – string

**Strictness**: `additionalProperties = false`

*Referenced by:*
• phase_schema.json → tasks[]
• module_schema.json → tasks[]

> Note: Older workflows using id/description instead of title/instruction will fail validation until migrated.


 --- 

## 3.3 module_schema.json

Defines a reusable module composed of multiple tasks.

Role

Allows cross-workflow sharing of task groups and logic.

Key Properties

Type: object
Required: module_id, title, tasks

• module_id – string
• title – string
• description – string
• tasks – array of task_schema.json
• dependencies – array of strings
• linked_phases – array of phase IDs
• metadata – $ref metadata_schema.json

Strictness: additionalProperties = false

Referenced by: workflow_schema.json → modules[]


---

# 4. Metadata & Evaluation Schemas


---

## 4.1 metadata_schema.json

Generic metadata for workflows, modules, or templates.

Role

Defines the official metadata surface for all SSWG artifacts.
Supports semantic lineage, purpose tracking, audience modeling, and tagging.

Key Properties

Type: object
Required: purpose, audience

• purpose – string (minLength: 3)
• audience – string
• author – string
• created – string (date-time)
• tags – array of strings
• context_level – enum: conceptual, procedural, evaluative

Strictness: additionalProperties = true
Metadata is intentionally extensible.

Referenced by:
• workflow_schema.json
• module_schema.json


---

## 4.2 evaluation_schema.json

Defines evaluation metrics used for scoring clarity, cohesion, completeness, etc.

Role

Provides structured scoring for workflow quality, recursive improvement logic, or CI evaluation.

Key Properties

Type: object
Required: clarity_score, completeness_score, cohesion_score

• clarity_score – number [0, 1]
• completeness_score – number [0, 1]
• cohesion_score – number [0, 1]
• semantic_alignment – number [0, 1]
• notes – string (free text)

Strictness: additionalProperties = true
Evaluation metrics are allowed to grow.

Referenced by:
• workflow_schema.json → evaluation
• phase_schema.json → evaluation_schema
• recursion_schema.json → evaluation_schema


---

# 5. Recursion & Semantic Schemas


---

## 5.1 recursion_schema.json

Defines deterministic recursion settings and regeneration rules.

Role

Formalizes the recursion model used by future ts/dtr recursive engines.

Key Properties

Type: object
Required: depth_limit, trigger_condition

• depth_limit – integer ≥ 1
• trigger_condition – string
• regeneration_threshold – number [0, 1]
• feedback_source – string
• evaluation_schema – $ref evaluation_schema.json
• history_log – array of strings

Strictness: additionalProperties = false

Referenced by: workflow_schema.json → recursion

Notes:
The runtime recursion manager (MVM) is simpler; this schema defines the final deterministic model.


---

## 5.2 semantics_schema.json

Defines semantic relations for terms used inside workflows.

Role

Enables semantic alignment, embedding comparisons, and ontology-level reasoning.

Key Properties

Type: object
Required: term, semantic_context

• term – string
• semantic_context – string
• related_terms – array of strings
• embedding_vector – array of numbers
• confidence – number [0, 1]

Strictness: additionalProperties = true

Referenced by: workflow_schema.json → semantics[]


---

# 6. Prompt & Ontology Schemas


---

## 6.1 prompt_schemas.json

Validates user prompts intended to generate workflows.

Role

Ensures predictable input structure for workflow-generation requests; enables adaptive or recursive modes.

Key Properties

Type: object
Required: purpose, target_audience, style

• purpose – string
• target_audience – enum: beginner, intermediate, expert
• delivery_mode – array of enums: text, code, visual, interactive
• expansion_mode – array: recursive, modular, adaptive
• evaluation_method – enum: self-refinement, peer-review, simulation
• style – enum: technical, friendly, wizardly, academic

Note: File currently plural (prompt_schemas.json). Renaming optional but suggested for canonical alignment.


---

## 6.2 ontology_schema.json

Defines a semantic/ontological view of a workflow.

Role

Used for high-level mapping, reasoning, clustering, and graph-based conceptual interpretation.

Key Properties

Required: workflow_id, purpose, target_audience, phases, dependency_graph

• workflow_id – string
• purpose – string
• target_audience – string
• phases – array of objects containing:
 id, title
 input / output arrays
 submodules
 ai_task_logic
 human_actionable
• dependency_graph – with nodes[] and edges[from,to]
• evaluation_metrics – array of strings

Use cases: semantic search, workflow comparison, conceptual graph building.


---

# 7. How Schemas Integrate Into the MVM Pipeline

Validation Layer

ai_validation/schema_validator.py

• Loads schemas from schemas/
• Uses Draft202012Validator
• Base URI is SCHEMAS_DIR.as_uri()
• Resolves all $ref entries relative to the schemas folder
• Rejects invalid workflows with detailed error traces

Generation Layer

generator/main.py

• Loads templates
• Validates against workflow_schema.json
• Draws dependency graphs
• Applies recursion/refinement (MVM/ts line)
• Emits JSON + Markdown artifacts

CI Enforcement

• Schema drift detection
• Version bump validation (MAJOR/MINOR/PATCH)
• Determinism tests for +dtr builds


---

# 8. Adding New Schemas (Canonical Procedure)

Steps required to introduce a new schema:

1. Create file under schemas/ with name *_schema.json
2. Set $schema to 2020-12 draft
3. Assign a canonical $id using the repository’s GitHub tree path
4. Use relative $ref only
5. Decide on strictness (additionalProperties)
6. Add regression examples under tests/resources/
7. Update schema.md (this document) to include the new schema



> *Any schema that participates in workflow generation requires a MINOR or MAJOR version bump depending on whether the change is backward-compatible.*


---

# 9. Determinism & Versioning Relationship

Because schemas define the public data contract, any modification to:

• required fields
• field names
• field types
• structural expectations

triggers a MAJOR version bump under SSWG versioning rules.

Additive, optional properties may be MINOR.
Internal reorganization without contract change is PATCH.


---

# 10. Summary

This directory is the authoritative definition of:

• workflows
• phases
• tasks
• modules
• recursion models
• semantic structures
• prompt formats
• ontologies

All schemas must remain consistent with SSWG’s transitive semantic model and determinism guarantees.
All modifications must follow versioning rules and validation protocols.


---
