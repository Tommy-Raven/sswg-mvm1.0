---
anchor:
  anchor_id: docs_telemetry_guide
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

sswg-mvm; version 1.0+ (living document)
Date: 12-22-2025
Document title: TELEMETRY_GUIDE.md
Author: Tommy Raven
Licensing: Raven Recordings ©️ see: *LICENSE.md*
(Document) Purpose: Outline how telemetry and structured logging expose recursion performance, with links to README.md and docs/README.md for navigation. Provide actionable setup steps, metrics descriptions, and integration notes so contributors can monitor new features safely. Clarify the expectations operators and contributors should follow when updating monitoring pipelines.

# Telemetry & Logging

Telemetry keeps recursive workflows observable in real time. Start with the platform descriptions in the root [README.md](../README.md) and navigation in [docs/README.md](./README.md), then use this guide to wire monitoring into new modules.

## Modules
- `ai_monitoring/telemetry.py` — collects runtime metrics emitted by recursion and evaluation components.
- `ai_monitoring/structured_logger.py` — writes structured JSON logs that mirror evolution records described in [docs/EVOLUTION_LOGGING.md](./EVOLUTION_LOGGING.md).
- `ai_monitoring/cli_dashboard.py` — renders live terminal dashboards for recursion depth, iteration speed, and quality metrics.

## Metrics tracked
- Recursion depth per workflow cycle
- Semantic delta score between iterations
- Workflow quality scores (clarity, expandability, translatability)
- Memory usage (MB) and cache hits
- Generation time per cycle
- Plugin execution counts to validate extensions built from [docs/PLUGIN_DEVELOPMENT.md](./PLUGIN_DEVELOPMENT.md)

## Example log payload
```json
{
  "iteration": 3,
  "depth": 2,
  "semantic_score": 0.87,
  "quality_score": 9.1,
  "memory_mb": 212,
  "generation_time_sec": 14.5,
  "timestamp": "2025-11-03T16:00Z"
}
```

## Integration guidance
- Emit telemetry alongside evolution logs so lineage analysis remains consistent across tools.
- Normalize field names with schemas in `schemas/` to simplify downstream parsing.
- Keep thresholds and alerting rules in configuration; document changes in PRs to help operators adjust dashboards.
- Validate output formats with local runs using the CLI dashboard before shipping changes.

## Operational checklist
- Verify log write permissions and retention settings wherever `ai_monitoring` stores artifacts.
- Ensure new metrics are explained in code comments and mirrored here for reviewers.
- Cross-link telemetry updates in `CHANGELOG.md` when they affect operators or SLOs.
