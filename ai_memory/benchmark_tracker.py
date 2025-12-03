#!/usr/bin/env python3
"""
ai_memory/benchmark_tracker.py — Benchmark tracking for SSWG MVM.

Tracks named benchmarks and their best scores over time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

from ai_monitoring.structured_logger import get_logger, log_event


@dataclass
class BenchmarkRecord:
    """
    Represents a single best-score record for a benchmark.
    """

    name: str
    score: float
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class BenchmarkTracker:
    """
    In-memory benchmark tracker.

    Behavior:
    - Stores only the best score seen per benchmark name.
    - Does not persist to disk by itself; callers can export `to_dict()`
      and store it via MemoryStore or other mechanisms.
    """

    def __init__(self) -> None:
        self._best: Dict[str, BenchmarkRecord] = {}
        self.logger = get_logger("benchmark")

    def record_run(
        self,
        name: str,
        score: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record a benchmark run and update the best record if the score
        improved.
        """
        timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        meta = dict(metadata or {})

        previous_record = self._best.get(name)
        improved = previous_record is None or score > previous_record.score

        # Log every run
        log_event(
            self.logger,
            "benchmark_record",
            {
                "name": name,
                "score": float(score),
                "improved": improved,
                "previous_score": previous_record.score if previous_record else None,
                "timestamp": timestamp,
                "metadata": meta,
            },
        )

        if improved:
            self._best[name] = BenchmarkRecord(
                name=name,
                score=float(score),
                timestamp=timestamp,
                metadata=meta,
            )
            log_event(
                self.logger,
                "benchmark_improved",
                {
                    "name": name,
                    "new_score": float(score),
                    "previous_score": previous_record.score
                    if previous_record
                    else None,
                    "timestamp": timestamp,
                },
            )

    def get_best(self, name: str) -> Optional[BenchmarkRecord]:
        """
        Return the best record seen for a benchmark, if any.
        """
        return self._best.get(name)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize all best benchmarks to a dict for export.
        """
        return {
            name: {
                "score": record.score,
                "timestamp": record.timestamp,
                "metadata": record.metadata,
            }
            for name, record in self._best.items()
        }
