#!/usr/bin/env python3
"""
ai_monitoring package — Telemetry and observability for SSWG MVM.

Public surface (MVM level):

- log_event(...) from structured_logger
- CLIDashboard for quick TUI summaries
- TelemetryLogger for lightweight structured event logging
- performance alert helpers (latency / error-rate oriented)
"""

from __future__ import annotations

from .structured_logger import log_event
from .telemetry import TelemetryLogger
from .performance_alerts import (
    check_latency_threshold,
    check_error_rate_threshold,
)

# CLIDashboard imported lazily in get_cli_dashboard to avoid hard dependency
# if users want a headless environment.


__all__ = [
    "log_event",
    "TelemetryLogger",
    "check_latency_threshold",
    "check_error_rate_threshold",
    "get_cli_dashboard",
]


def get_cli_dashboard():
    """
    Return a CLIDashboard instance if available, or a no-op stub.

    This avoids import-time failures in environments where the dashboard
    is not wired or not desired.
    """
    try:
        from .cli_dashboard import CLIDashboard  # type: ignore
    except Exception:  # pragma: no cover - defensive stub

        class CLIDashboard:  # type: ignore[no-redef]
            def record_cycle(self, success: bool) -> None:
                pass

            def record_phase(self, phase_id: str, success: bool) -> None:
                pass

            def render(self) -> None:
                pass

    return CLIDashboard()


def get_version() -> str:
    """
    Simple version identifier for the monitoring subsystem.
    """
    return "ai_monitoring-mvm-0.1.0"
