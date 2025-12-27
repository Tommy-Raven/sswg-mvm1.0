#!/usr/bin/env python3
"""
ai_memory/benchmark_tracker.py — Benchmark tracking for SSWG MVM.

Tracks named benchmarks and their best scores over time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

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


@dataclass(frozen=True)
class BenchmarkDefinition:
    """
    Defines a benchmark dataset and acceptance criteria.
    """

    name: str
    dataset_description: str
    metric_name: str
    expected_range: Tuple[float, float]
    acceptance_criteria: str
    unit: str = "score"


CALIBRATION_BENCHMARKS: Dict[str, BenchmarkDefinition] = {
    "calibration.clarity.core_v1": BenchmarkDefinition(
        name="calibration.clarity.core_v1",
        dataset_description=(
            "50 curated workflow prompts spanning ingest→log, balanced across"
            " new and existing module patterns."
        ),
        metric_name="clarity",
        expected_range=(0.82, 0.94),
        acceptance_criteria="Median ≥ 0.86 and p10 ≥ 0.80.",
        unit="score",
    ),
    "calibration.expandability.core_v1": BenchmarkDefinition(
        name="calibration.expandability.core_v1",
        dataset_description=(
            "30 modularization exercises covering adapter swaps, schema overlays,"
            " and phase extension patterns."
        ),
        metric_name="expandability",
        expected_range=(0.74, 0.90),
        acceptance_criteria="Median ≥ 0.78 and p10 ≥ 0.70.",
        unit="score",
    ),
    "calibration.translatability.core_v1": BenchmarkDefinition(
        name="calibration.translatability.core_v1",
        dataset_description=(
            "24 workflows rendered across Markdown/JSON/API forms, verifying"
            " fidelity of conversion."
        ),
        metric_name="translatability",
        expected_range=(0.80, 0.95),
        acceptance_criteria="Median ≥ 0.85 and p10 ≥ 0.78.",
        unit="score",
    ),
    "calibration.recursive_alignment.core_v1": BenchmarkDefinition(
        name="calibration.recursive_alignment.core_v1",
        dataset_description=(
            "20 multi-iteration recursion runs with lineage checkpoints and"
            " phase-boundary compliance."
        ),
        metric_name="recursive_alignment",
        expected_range=(0.75, 0.92),
        acceptance_criteria="Median ≥ 0.80 and p10 ≥ 0.72.",
        unit="score",
    ),
}


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

    def get_definitions(self) -> Dict[str, BenchmarkDefinition]:
        """
        Return the known calibration benchmark definitions.
        """
        return dict(CALIBRATION_BENCHMARKS)
