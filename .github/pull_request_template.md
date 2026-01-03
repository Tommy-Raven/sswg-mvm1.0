---
anchor:
  anchor_id: github_pull_request_template
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---


SSWG Pull Request Template

🧾 PR Title

<!-- Short, descriptive title. Example: “Fix phase-schema resolver + update PDL metadata rules” -->
---

📘 Summary

Describe what this PR does.
Explain what was changed, why, and how it affects SSWG-MVM.
If this PR modifies generator logic, schema definitions, workflow templates, PDL, or meta-knowledge, call that out directly.


---

🧪 Type of Change

Select all that apply:

[ ] Feature: Adds new module, workflow logic, or generator capability

[ ] Fix: Corrects behavior, schema drift, or recursion-engine issue

[ ] Refactor: Structural improvement, renaming, consolidation

[ ] Documentation: Updates to /docs, READMEs, or Grim-Tomes

[ ] CI/CD: GitHub Actions, validation pipelines, dependency bumps

[ ] Schema: Updates to JSON Schema, PDL, metadata headers

[ ] Other (explain below)



---

📂 Modified Components

List the primary directories touched:

[ ] generator/

[ ] ai_core/ / grim_core/

[ ] ai_recursive/

[ ] ai_evaluation/

[ ] ai_validation/

[ ] ai_memory/

[ ] ai_graph/

[ ] schemas/

[ ] data/templates/

[ ] docs/

[ ] config/

[ ] .github/workflows/



---

🏗️ Detailed Description

Provide a clear explanation of:

1. What was implemented or changed


2. Why the change was needed


3. How it integrates into the SSWG workflow pipeline


4. Any known implications for future recursion, schema versioning, or CI



Use technical language here—this is for system maintainers.


---

🧬 Schema / PDL Impact

Does this PR modify any of the following?

[ ] JSON Schemas (workflow_schema.json, phase_schema.json, etc.)

[ ] PDL phase definitions

[ ] Metadata header patterns

[ ] Canonical $id or $ref mappings

[ ] Validation logic


If yes, describe the change and its compatibility impact:

Summary:
Compatibility:
Migration needed:


---

🔁 Recursion & Versioning Impact

Does this affect:

Workflow regeneration logic?

Version-migration logic?

Phase expansion heuristics?

Recursive safety limits or guards?


Explain:

Recursion impact:
Versioning impact:
Safety considerations:


---

🧪 Tests

[ ] Added tests

[ ] Updated existing tests

[ ] No tests required


Describe coverage:

Test summary:


---

🧰 Validation Checklist (required)

Before requesting review, ensure:

[ ] pytest passes locally

[ ] Linting passes (ruff, flake8, or project standard)

[ ] JSON schemas validate using the local schema validator

[ ] All modified workflow JSON files pass schema validation

[ ] GitHub Actions workflows still execute without errors

[ ] No unintentional schema drift occurred



---

📸 Screenshots / Logs (optional)

Attach visualization outputs, recursion logs, test summaries, diagrams, etc.


---

🗣️ Reviewer Notes

Anything reviewers should pay special attention to?
List breaking changes or migration instructions here.


---

✔️ Final Review Checklist

[ ] Code style and formatting meets project standards

[ ] No debug prints or temporary files

[ ] Dependencies updated intentionally

[ ] Documentation updated where required

[ ] Ready for merge
