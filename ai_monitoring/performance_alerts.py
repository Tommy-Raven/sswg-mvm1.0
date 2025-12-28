#!/usr/bin/env python3
"""
ai_monitoring/performance_alerts.py — Simple performance checks for SSWG MVM.

This module provides small, composable helpers to check basic performance
conditions such as latency and error rate. It is intentionally lightweight
and side-effect free; callers decide how to emit logs or alerts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class AlertResult:
    ok: bool
    metric: str
    value: float
    threshold: float
    message: str


def check_latency_threshold(duration_ms: float, max_ms: float) -> AlertResult:
    """
    Check whether a given latency (in ms) stays below a maximum threshold.

    Args:
        duration_ms: Observed latency in milliseconds.
        max_ms: Maximum acceptable latency.

    Returns:
        AlertResult indicating pass/fail.
    """
    ok = duration_ms <= max_ms
    msg = (
        f"Latency OK: {duration_ms:.2f} ms ≤ {max_ms:.2f} ms"
        if ok
        else f"Latency HIGH: {duration_ms:.2f} ms > {max_ms:.2f} ms"
    )
    return AlertResult(
        ok=ok,
        metric="latency_ms",
        value=duration_ms,
        threshold=max_ms,
        message=msg,
    )


def check_error_rate_threshold(
    errors: int,
    total: int,
    max_rate: float,
) -> AlertResult:
    """
    Check whether error rate (errors / total) stays below a maximum threshold.

    Args:
        errors: Number of failed operations.
        total: Total number of operations.
        max_rate: Maximum acceptable error rate (0.0–1.0).

    Returns:
        AlertResult indicating pass/fail.
    """
    rate = 0.0 if total == 0 else errors / max(total, 1)
    ok = rate <= max_rate
    msg = (
        f"Error rate OK: {rate:.3f} ≤ {max_rate:.3f}"
        if ok
        else f"Error rate HIGH: {rate:.3f} > {max_rate:.3f}"
    )
    return AlertResult(
        ok=ok,
        metric="error_rate",
        value=rate,
        threshold=max_rate,
        message=msg,
    )


# End of ai_monitoring/performance_alerts.py
