> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

---
anchor:
  anchor_id: docs_evolution_logging
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

sswg-mvm; version 1.0+ (living document)
Date: 12-22-2025
Document title: EVOLUTION_LOGGING.md
Author: Tommy Raven
Licensing: Raven Recordings ©️ see: *LICENSE.md*
(Document) Purpose: Describe how the recursion stack records lineage, metrics, and artifacts so contributors can debug and reproduce runs. Connects the logging pathways to the repository overviews in README.md and docs/README.md, and clarifies how telemetry and evaluation modules consume these logs. Provides concrete storage conventions and usage guidance for new workflows.

# Evolution Logging

The evolution logging pipeline keeps recursive workflows observable and reproducible. High-level entrypoints live in the root [README.md](../README.md), with documentation navigation in [docs/README.md](./README.md). This guide details how the logging pieces fit together and where to extend them.

## Architecture overview
- **Sources:** `ai_memory.store`, `ai_recursive.expansion`, and `ai_conductor.workflow` emit events for every recursion pass.
- **Formats:** JSON for machine pipelines and Markdown for human review (mirrors the patterns in [docs/TELEMETRY_GUIDE.md](./TELEMETRY_GUIDE.md)).
- **Storage:** Persistent artifacts land in `ai_memory/outputs/` with deterministic version IDs and lineage references.
- **Schemas:** Metadata shapes align with `schemas/workflow_schema.json` and the recursion expectations in [docs/ARCHITECTURE.md](./ARCHITECTURE.md).

## Traceability and versioning
- Each refinement pass writes a new versioned record with parent-child links maintained by `ai_memory.lineage`.
- Deterministic hashes anchor artifacts so runs are reproducible across environments.
- Lineage graphs are validated against the graph constraints outlined in [docs/RECURSION_MANAGER.md](./RECURSION_MANAGER.md).
- Logs carry provenance fields (author, timestamp, model, configuration) to meet auditability requirements.

## Metrics capture
- `ai_memory.metrics` tracks clarity, coverage, expandability, translatability, and execution duration for each iteration.
- Metrics co-travel with workflow outputs for later semantic analysis (see [docs/SEMANTIC_ANALYSIS.md](./SEMANTIC_ANALYSIS.md)).
- Telemetry sinks mirror these values for live dashboards and alarms described in [docs/TELEMETRY_GUIDE.md](./TELEMETRY_GUIDE.md).

## API examples
```python
from ai_memory.store import save_workflow
from ai_memory.lineage import get_lineage
from ai_memory.metrics import aggregate_metrics

record_id = save_workflow(workflow_obj, version="v1.0.3")
lineage = get_lineage(workflow_id="WF-20251130-001")
metrics = aggregate_metrics(workflow_id="WF-20251130-001")
```

## Best practices
- Log every recursion iteration, including failures, to preserve context for debugging.
- Keep phase-level timestamps so the telemetry stack can surface performance regressions.
- Align metric names with the evaluation taxonomy in `ai_evaluation` to simplify comparisons.
- Archive older logs instead of deleting them—backward analysis supports optimization work called out in [docs/OPTIMIZATION_PLAN.md](./OPTIMIZATION_PLAN.md).

## Onboarding checklist
- Familiarize yourself with the navigation and terminology in [docs/README.md](./README.md).
- Trace a sample run end-to-end: generate a workflow, refine it, inspect JSON + Markdown logs, and view lineage graphs.
- When proposing changes, document the expected log shape and fields in your PR description for reviewers.
