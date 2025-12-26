# ai_evaluation — Quality, Scoring, and Semantic Checks (SSWG MVM)

The `ai_evaluation` package is responsible for assigning *quality signals*
to workflows and their outputs. At the MVM stage, the goals are:

- Provide a small set of **interpretable** metrics.
- Keep evaluation composable and side-effect free.
- Make it easy to plug in external scorers (LLMs, classifiers, etc.) later.

---

## Components

### 1. `evaluation_engine.py`

**Role:** High-level orchestration of quality metrics.

Responsibilities:

- Accept a workflow dict (schema-aligned).
- Run a set of metric functions from `quality_metrics.py` against:
  - metadata
  - phases/modules
  - outputs
- Return a structured result, e.g.:

```jsonc
{
  "overall_score": 0.86,
  "metrics": {
    "coverage": 0.9,
    "coherence": 0.8,
    "specificity": 0.85
  }
}
```

### 2. `checkpoints.py`

**Role:** Capture evaluation checkpoints for each iteration.

Responsibilities:

- Define success criteria per checkpoint (defaults: overall_score ≥ 0.55, clarity/coverage ≥ 0.5).
- Flag regressions between checkpoints and surface rollback recommendations.
- Produce compact summaries for attachment to `workflow["evaluation"]["checkpoints"]`.
