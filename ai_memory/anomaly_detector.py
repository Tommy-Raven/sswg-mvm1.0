#!/usr/bin/env python3
"""
ai_memory/anomaly_detector.py — Basic anomaly detection for SSWG MVM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from typing import Iterable, List


@dataclass
class AnomalyDetector:
    """
    Simple z-score-based anomaly detector.

    Usage:
        detector = AnomalyDetector(n_sigma=3.0)
        detector.fit([0.8, 0.82, 0.79, 0.81])
        detector.is_anomalous(0.5)
    """

    n_sigma: float = 3.0
    mean: float = 0.0
    std: float = 0.0
    _fitted: bool = field(default=False, init=False)

    def fit(self, values: Iterable[float]) -> "AnomalyDetector":
        """
        Fit the detector to a sequence of numeric values by computing mean
        and standard deviation.
        """
        numeric_values: List[float] = [float(value) for value in values]
        if not numeric_values:
            self.mean = 0.0
            self.std = 0.0
            self._fitted = False
            return self

        count = len(numeric_values)
        self.mean = sum(numeric_values) / count
        variance = sum((value - self.mean) ** 2 for value in numeric_values) / max(
            1, count - 1
        )
        self.std = sqrt(variance)
        self._fitted = True
        return self

    def score(self, value: float) -> float:
        """
        Return the absolute z-score of a value with respect to the fitted
        distribution. Returns 0.0 if the detector is not fitted.
        """
        if not self._fitted or self.std == 0.0:
            return 0.0
        return abs((value - self.mean) / self.std)

    def is_anomalous(self, value: float) -> bool:
        """
        True if the value is more than `n_sigma` standard deviations away
        from the mean.
        """
        return self.score(value) > self.n_sigma
