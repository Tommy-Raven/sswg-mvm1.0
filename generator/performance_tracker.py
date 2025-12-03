#!/usr/bin/env python3
"""
generator/performance_tracker.py — Track phase timing and performance.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from ai_monitoring.structured_logger import get_logger, log_event


@dataclass
class PhaseStats:
    """Aggregate statistics for a single phase label."""
    count: int = 0
    total_duration: float = 0.0
    failures: int = 0

    def record(self, duration: float, success: bool) -> None:
        """Update stats with a single run."""
        self.count += 1
        self.total_duration += duration
        if not success:
            self.failures += 1

    @property
    def average_duration(self) -> float:
        """Return average duration in seconds."""
        if self.count == 0:
            return 0.0
        return self.total_duration / self.count

    @property
    def failure_rate(self) -> float:
        """Return failure rate in [0, 1]."""
        if self.count == 0:
            return 0.0
        return self.failures / self.count


class PerformanceTracker:
    """
    Track timing and basic performance metrics for generator phases.
    """

    def __init__(self) -> None:
        self._stats: Dict[str, PhaseStats] = {}
        self._logger = get_logger("performance")

    def track(self, label: str):
        """Context manager for timing a named phase."""
        return _TimingContext(self, label)

    def _record(self, label: str, duration: float, success: bool = True) -> None:
        stats = self._stats.setdefault(label, PhaseStats())
        stats.record(duration, success)
        log_event(
            self._logger,
            "phase_timing",
            {
                "label": label,
                "duration_sec": duration,
                "success": success,
                "count": stats.count,
                "avg_duration_sec": stats.average_duration,
                "failure_rate": stats.failure_rate,
            },
        )

    def snapshot(self) -> Dict[str, Any]:
        """Return a serializable snapshot of all tracked metrics."""
        return {
            label: {
                "count": stats.count,
                "total_duration_sec": stats.total_duration,
                "avg_duration_sec": stats.average_duration,
                "failures": stats.failures,
                "failure_rate": stats.failure_rate,
            }
            for label, stats in self._stats.items()
        }


class _TimingContext:
    """Internal context manager for PerformanceTracker."""

    def __init__(self, tracker: PerformanceTracker, label: str) -> None:
        self._tracker = tracker
        self._label = label
        self._start: Optional[float] = None
        self._success: bool = True

    def __enter__(self) -> "_TimingContext":
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        end = time.perf_counter()
        duration = end - (self._start or end)
        self._success = exc is None
        self._tracker._record(self._label, duration, self._success)
