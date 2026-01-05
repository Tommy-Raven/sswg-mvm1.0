> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

---
anchor:
  anchor_id: docs_semantic_analysis
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

sswg-mvm; version 1.0+ (living document)
Date: 12-22-2025
Document title: SEMANTIC_ANALYSIS.md
Author: Tommy Raven
Licensing: Raven Recordings ©️ see: *LICENSE.md*
(Document) Purpose: Explain how sswg-mvm measures semantic change across recursion cycles and how those scores influence stopping conditions. Provide guidance linked to README.md and docs/README.md so contributors can align evaluation work with the broader architecture. Include practical thresholds, integration notes, and extension hooks.

# Semantic Analysis & Scoring

Semantic analysis evaluates whether a new recursion output meaningfully differs from prior iterations. Start with the system introductions in the root [README.md](../README.md) and [docs/README.md](./README.md), then use this guide to align evaluation changes.

## Goals
- Detect material differences between iterations and prevent unnecessary rewrites when content stabilizes.
- Supply delta metrics to the recursion manager and telemetry stack so convergence is transparent.
- Keep scores consistent with evaluation taxonomies outlined in `ai_evaluation` and documented in [docs/METRICS_SYSTEM.md](./METRICS_SYSTEM.md).

## Scoring signals
- **Embedding similarity:** cosine similarity or dot-product scores computed via `generator.semantic_scorer.SemanticScorer`.
- **Edit distance:** Levenshtein-based character or token deltas for markdown-heavy outputs.
- **Structural drift:** optional checks for step reordering or DAG edge changes paired with the validators in `ai_graph`.

### Formula example
```
Semantic Delta = 1 - Similarity(Old_Output, New_Output)
```
The similarity function should be deterministic and documented in code comments to aid reproducibility.

## Integration flow
```python
from generator.semantic_scorer import SemanticScorer

scorer = SemanticScorer()
score = scorer.compare(text_a, text_b)

if score < 0.15:
    stop_recursion()
```
- Thresholds should be stored in configuration (`config/`) and referenced in PR descriptions when adjusted.
- Semantic deltas feed into logs managed in [docs/EVOLUTION_LOGGING.md](./EVOLUTION_LOGGING.md) and telemetry dashboards in [docs/TELEMETRY_GUIDE.md](./TELEMETRY_GUIDE.md).

## Practices for contributors
- Add unit tests that freeze model seeds or fixture text to guarantee consistent scoring outcomes.
- Document new similarity functions in both code docstrings and this file so downstream teams know how to interpret values.
- When tuning thresholds, reference the recursion controls in [docs/architecture/recursion_engine.md](./architecture/recursion_engine.md) to keep behavior predictable.
- Surface outliers in the evolution logs so reviewers can correlate semantic spikes with specific code changes.
