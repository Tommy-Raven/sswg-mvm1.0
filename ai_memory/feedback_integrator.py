#!/usr/bin/env python3
"""
ai_memory/feedback_integrator.py
Grimoire / SSWG MVM — Feedback Integration & Long-Term Memory Engine

Aggregates historical feedback, regeneration outcomes, and evaluation
metrics into a persistent knowledge base. Used to:
- Track diff complexity over time
- Track clarity scores
- Adapt regeneration thresholds based on historical performance
"""

from __future__ import annotations

import json
import os
import statistics
from datetime import datetime
from typing import Any, Dict, List

from ai_monitoring.structured_logger import get_logger, log_event


class FeedbackIntegrator:
    """
    Persist and aggregate feedback from diff cycles and evaluations.

    Responsibilities:
    - Store per-cycle records (diff size, clarity, regeneration flag).
    - Maintain a history of clarity scores.
    - Adapt the regeneration threshold based on average clarity.
    """

    def __init__(self, path: str = "./data/feedback_log.json") -> None:
        self.path = path
        self.logger = get_logger("feedback")
        self.feedback_data: Dict[str, Any] = self._load_feedback()

    # ---------------------- Internal Helpers ---------------------- #

    def _load_feedback(self) -> Dict[str, Any]:
        """Load or initialize persistent feedback data."""
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as file_handle:
                    data = json.load(file_handle)
                # Ensure minimal structure exists
                data.setdefault("records", [])
                data.setdefault("regeneration_threshold", 2)
                data.setdefault("clarity_scores", [])
                data.setdefault("average_clarity", None)
                return data
            except (OSError, json.JSONDecodeError):
                # Corrupt or unreadable file → reset structure
                pass

        return {
            "records": [],
            "regeneration_threshold": 2,
            "clarity_scores": [],
            "average_clarity": None,
        }

    def _save_feedback(self) -> None:
        """Persist current feedback data to disk."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as file_handle:
            json.dump(self.feedback_data, file_handle, indent=2)

    # ---------------------- Core Methods ---------------------- #

    def record_cycle(
        self,
        diff_summary: Dict[str, Any],
        evaluation_metrics: Dict[str, Any],
        regenerated: bool,
    ) -> None:
        """
        Log the outcome of a regeneration or evaluation cycle.

        Args:
            diff_summary: Output of version_diff_engine.compute_diff_summary.
            evaluation_metrics: e.g. {"clarity_score": float, ...}.
                                Assumed to be in [0.0, 1.0] for clarity_score.
            regenerated: True if a regeneration was performed this cycle.
        """
        clarity_score = evaluation_metrics.get("clarity_score")

        record = {
            "timestamp": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "diff_size": int(diff_summary.get("diff_size", 0)),
            "regeneration_triggered": bool(regenerated),
            "clarity_score": clarity_score,
            "changed_fields": len(diff_summary.get("changed_fields", [])),
            "added_phases": len(diff_summary.get("added_phases", [])),
            "removed_phases": len(diff_summary.get("removed_phases", [])),
            "modified_phases": len(diff_summary.get("modified_phases", [])),
        }

        self.feedback_data["records"].append(record)
        self.feedback_data["clarity_scores"].append(clarity_score)

        log_event(self.logger, "feedback_recorded", record)

        self._recalculate_threshold()
        self._save_feedback()

    def _recalculate_threshold(self) -> None:
        """
        Dynamically adjust regeneration threshold based on historical
        clarity and diff complexity.

        Assumes clarity_scores are in [0.0, 1.0]:
        - >= 0.9 → threshold = 3
        - >= 0.7 → threshold = 2
        - else   → threshold = 1
        """
        raw_scores: List[Any] = self.feedback_data.get("clarity_scores", [])
        # Filter out None and coerce to float so Pylance / statistics are happy
        clarity_scores: List[float] = [
            float(score) for score in raw_scores if score is not None
        ]
        if not clarity_scores:
            return

        average_clarity = statistics.mean(clarity_scores)
        self.feedback_data["average_clarity"] = round(average_clarity, 3)

        if average_clarity >= 0.9:
            threshold = 3
        elif average_clarity >= 0.7:
            threshold = 2
        else:
            threshold = 1

        self.feedback_data["regeneration_threshold"] = threshold

        log_event(
            self.logger,
            "threshold_adjusted",
            {
                "new_threshold": threshold,
                "average_clarity": average_clarity,
            },
        )

    # ---------------------- Accessor Methods ---------------------- #

    def get_summary(self) -> Dict[str, Any]:
        """Return current learning status."""
        total_cycles = len(self.feedback_data.get("records", []))
        average_clarity = self.feedback_data.get("average_clarity")
        threshold = self.feedback_data.get("regeneration_threshold")
        return {
            "total_cycles": total_cycles,
            "average_clarity": average_clarity,
            "adaptive_threshold": threshold,
        }


if __name__ == "__main__":
    integrator = FeedbackIntegrator()

    fake_diff = {
        "diff_size": 3,
        "changed_fields": ["metadata.title"],
        "added_phases": ["Phase 3"],
        "removed_phases": [],
        "modified_phases": [],
    }

    # Example clarity in [0, 1]
    fake_eval = {"clarity_score": 0.86}

    integrator.record_cycle(fake_diff, fake_eval, regenerated=True)
    SUMMARY = integrator.get_summary()

    print("\n📚 Feedback Summary")
    print(SUMMARY)
