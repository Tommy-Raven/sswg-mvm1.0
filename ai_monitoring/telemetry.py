#!/usr/bin/env python3
"""
ai_monitoring/telemetry.py — Semantic telemetry for SSWG MVM.

This module provides a small, class-based API on top of `structured_logger`
for recording semantic events. It is intentionally thin at the MVM stage.

Usage:

    from ai_monitoring.telemetry import TelemetryLogger

    telemetry = TelemetryLogger()
    telemetry.record("workflow_start", {"workflow_id": "wf_001"})
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .structured_logger import log_event


class TelemetryLogger:
    """
    Lightweight semantic telemetry wrapper.

    At MVM:
    - simply delegates to `log_event`.
    - preserves event names & payloads as-is.

    In later versions, this can:
    - attach workflow/session IDs automatically
    - multiplex to additional sinks (metrics, traces, etc.)
    """

    def __init__(self, default_context: Optional[Dict[str, Any]] = None) -> None:
        self.default_context: Dict[str, Any] = default_context or {}

    def record(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a telemetry event.

        Args:
            event: Short event name (e.g. "workflow_start").
            data: Optional payload dict.
        """
        payload = dict(self.default_context)
        if data:
            payload.update(data)

        log_event(event, payload)


# End of ai_monitoring/telemetry.py
