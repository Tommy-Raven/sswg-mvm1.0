> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

---
anchor:
  anchor_id: docs_plugin_development
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

sswg-mvm; version 1.0+ (living document)
Date: 12-22-2025
Document title: PLUGIN_DEVELOPMENT.md
Author: Tommy Raven
Licensing: Raven Recordings ©️ see: *LICENSE.md*
(Document) Purpose: Show how to extend sswg-mvm through plugins without destabilizing the recursion or evaluation stacks. Tie guidance back to repository entrypoints in README.md and docs/README.md, highlighting structure, registration, testing, and safety expectations. Set expectations for documentation and validation so reviewers can evaluate new hooks quickly.

# Plugin Development Guide

Plugins let teams extend **sswg-mvm** without touching core orchestration. Review the system overview in the root [README.md](../README.md) and documentation map in [docs/README.md](./README.md) before wiring new hooks.

## Plugin structure
```python
# Example: custom_plugin.py
from generator.plugin_loader import register_plugin

@register_plugin(name="CustomMetric")
def custom_quality_metric(workflow):
    """Compute a custom quality metric for a workflow."""
    score = len(workflow.steps) / 10
    return {"custom_score": score}
```

## Loading plugins
Declare plugins in configuration to keep startup deterministic:
```yaml
# config/settings.yml
plugins:
  - custom_plugin
  - another_plugin
```
The loader imports and registers each plugin at startup. Hooks can target:
- Evaluation cycles in `ai_evaluation`
- Recursive expansions in `ai_recursive`
- Workflow phases under `ai_conductor/phases`
- Telemetry enrichers in `ai_monitoring`

## Development guidelines
- **Isolation:** Do not mutate core modules or global state; return new objects where possible.
- **Idempotence:** Ensure repeated calls produce consistent outputs, aiding reproducibility and logging.
- **Documentation:** Include docstrings, examples, and an entry in this file describing purpose and inputs.
- **Error handling:** Catch expected exceptions and log via `ai_monitoring.structured_logger` without stopping recursion.
- **Versioning:** Track plugin versions and compatibility notes in your README snippet or config comments.

## Testing plugins
- Place tests in `tests/plugins/` using pytest; mirror fixtures described in [docs/QUICKSTART.md](./QUICKSTART.md).
- Validate outputs against known workflows and semantic scores to avoid regressions in [docs/SEMANTIC_ANALYSIS.md](./SEMANTIC_ANALYSIS.md).
- Exercise logging and telemetry integration so dashboards described in [docs/TELEMETRY_GUIDE.md](./TELEMETRY_GUIDE.md) stay accurate.

## Example: workflow transformer
```python
from generator.plugin_loader import register_plugin

@register_plugin(name="StepNormalizer")
def normalize_steps(workflow):
    """Standardize step IDs and trim whitespace."""
    for i, step in enumerate(workflow.steps):
        step["id"] = i + 1
        step["text"] = step["text"].strip()
    return workflow
```
This transformer keeps DAG edges stable and readable for downstream analysis and logging.

## Next steps
- Add additional plugin hooks for API exposure or CLI tooling.
- Document plugin-specific configuration keys in `config/settings.yml` to aid operators.
- Consider sandboxing or feature flags for untrusted plugins to align with practices in [docs/SECURITY.md](./SECURITY.md).
