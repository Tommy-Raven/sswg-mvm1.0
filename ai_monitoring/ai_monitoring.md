---
anchor:
  anchor_id: ai_monitoring_ai_monitoring
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# ai_monitoring — Telemetry & Observability for SSWG MVM

The `ai_monitoring` package is the observability layer of SSWG:

- Emits structured events for key actions (generation, validation, recursion).
- Tracks performance characteristics (latency, error rates).
- Provides a minimal CLI dashboard for human-friendly summaries.

At the MVM stage, the focus is on **low-friction, low-coupling** monitoring:
easy to call, safe to ignore, and simple to extend.

---

## Components

### 1. `structured_logger.py`

**Role:** Canonical structured logging entrypoint.

- Provides:
  - `log_event(event: str, payload: dict | None = None)` — new MVM style.
  - Backwards-compatible signature:
    - `log_event(logger, event: str, data: dict | None = None)`
- Writes to both console and `./logs/workflow.log`.
- Used by:
  - generator
  - ai_core
  - ai_validation
  - history, exporters, etc.

This is the lowest-level, always-safe logging primitive.

---

### 2. `telemetry.py`

**Role:** Higher-level `TelemetryLogger` abstraction for semantic events.

Intended behavior:

- Wraps `log_event` with a compact, class-based API:
  - `TelemetryLogger.record(event_name: str, data: dict | None = None)`
- Can later support:
  - multi-sink telemetry (JSONL, OpenTelemetry, metrics backends)
  - correlation IDs for workflow sessions

At MVM, this is a very thin convenience wrapper.

---

### 3. `cli_dashboard.py`

**Role:** Lightweight TUI-ish dashboard for local runs.

Responsibilities:

- Track:
  - workflow cycles (success/failure)
  - phases executed
- Render a short summary at the end of orchestration.

The ai_core `Orchestrator` uses this to provide a quick “what just happened?”
view during development. In non-interactive environments, this can be turned
into a no-op.

*(Implementation lives in `cli_dashboard.py`, which should maintain a small
public surface: `record_cycle`, `record_phase`, `render`.)*

---

### 4. `performance_alerts.py`

**Role:** Simple health checks and thresholds.

MVM responsibilities:

- Provide helpers like:
  - `check_latency_threshold(duration, limit_ms)`
  - `check_error_rate_threshold(error_count, total, max_rate)`
- Return structured results that higher-level components can turn into
  log entries, alerts, or status flags.

This is where early “red flag” logic for performance lives.

---

## MVM Philosophy for Monitoring

- **Non-fatal:** monitoring should not crash core logic if it breaks.
- **Layered:** use `log_event` for low-level logging; `TelemetryLogger`
  for semantic events; higher-level tools for dashboards/alerts.
- **Incremental:** it should be easy to add new event types without
  rewriting the world.

Update this document as the monitoring stack becomes more sophisticated.
