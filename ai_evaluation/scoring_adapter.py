#!/usr/bin/env python3
"""
ai_evaluation/scoring_adapter.py — Score normalization utilities for SSWG MVM.

Provides a small adapter class to normalize arbitrary raw scores into a
standard 0–1 range and clip outliers.

Intended for:
- LLM-based scoring functions
- classifier confidences
- heuristic scores on arbitrary scales
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class ScoreAdapter:
    """
    Normalize raw scores to a [0, 1] range.

    Strategies:

    - min_max:
        scales based on observed min/max over a reference set
    - clip:
        clip to given low/high bounds and rescale

    For MVM, we implement a simple min/max strategy.
    """

    min_score: float = 0.0
    max_score: float = 1.0

    def fit(self, scores: Iterable[float]) -> "ScoreAdapter":
        """
        Fit the adapter to a reference set of scores.
        """
        scores_list: List[float] = list(scores)
        if not scores_list:
            return self
        self.min_score = min(scores_list)
        self.max_score = max(scores_list)
        if self.min_score == self.max_score:
            # Avoid division by zero, widen artificially
            self.min_score -= 0.5
            self.max_score += 0.5
        return self

    def transform(self, score: float) -> float:
        """
        Normalize a single score to [0, 1].
        """
        if self.max_score == self.min_score:
            return 0.5
        normalized = (score - self.min_score) / (self.max_score - self.min_score)
        # Clip just in case
        if normalized < 0.0:
            return 0.0
        if normalized > 1.0:
            return 1.0
        return normalized

    def fit_transform(self, score: float, ref_scores: Iterable[float]) -> float:
        """
        Convenience: fit on reference scores, then transform a single score.
        """
        self.fit(ref_scores)
        return self.transform(score)


# End of ai_evaluation/scoring_adapter.py
