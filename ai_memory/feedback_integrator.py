#!/usr/bin/env python3
"""
ai_memory/feedback_integrator.py
Grimoire v4.8 — Feedback Integration & Long-Term Memory Engine
This module aggregates historical feedback, regeneration outcomes,
and evaluation metrics into a persistent knowledge base.
It allows Grimoire to learn over multiple diff cycles, detect recurring
weaknesses or strengths, and adjust regeneration thresholds adaptively.
"""

import os
import json
import statistics
from datetime import datetime
from ai_monitoring.structured_logger import get_logger, log_event


class FeedbackIntegrator:
    def __init__(self, path: str = "./data/feedback_log.json"):
        self.path = path
        self.logger = get_logger()
        self.feedback_data = self._load_feedback()

    # ---------------------- Internal Helpers ---------------------- #

    def _load_feedback(self):
        """Load or initialize persistent feedback data."""
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {
                "records": [],
                "regeneration_threshold": 2,
                "clarity_scores": [],
                "average_clarity": None
            }

    def _save_feedback(self):
        """Persist current feedback data to disk."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.feedback_data, f, indent=2)

    # ---------------------- Core Methods ---------------------- #

    def record_cycle(self, diff_summary: dict, evaluation_metrics: dict, regenerated: bool):
        """
        Log the outcome of a regeneration or evaluation cycle.
        Stores diff metrics, clarity scores, and regeneration triggers.
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "diff_size": diff_summary.get("diff_size", 0),
            "regeneration_triggered": regenerated,
            "clarity_score": evaluation_metrics.get("clarity_score"),
            "changed_fields": len(diff_summary.get("changed_fields", [])),
            "added_phases": len(diff_summary.get("added_phases", [])),
            "removed_phases": len(diff_summary.get("removed_phases", [])),
            "modified_phases": len(diff_summary.get("modified_phases", []))
        }

        self.feedback_data["records"].append(record)
        self.feedback_data["clarity_scores"].append(record["clarity_score"])
        log_event(self.logger, "feedback_recorded", record)
        self._recalculate_threshold()
        self._save_feedback()

    def _recalculate_threshold(self):
        """
        Dynamically adjust regeneration threshold based on
        historical clarity and diff complexity.
        """
        clarity_scores = [c for c in self.feedback_data["clarity_scores"] if c is not None]
        if not clarity_scores:
            return

        avg_clarity = statistics.mean(clarity_scores)
        self.feedback_data["average_clarity"] = round(avg_clarity, 2)

        # Adaptive logic: as clarity improves, threshold rises to prevent over-regeneration
        if avg_clarity >= 9.0:
            self.feedback_data["regeneration_threshold"] = 3
        elif avg_clarity >= 7.0:
            self.feedback_data["regeneration_threshold"] = 2
        else:
            self.feedback_data["regeneration_threshold"] = 1

        log_event(self.logger, "threshold_adjusted", {
            "new_threshold": self.feedback_data["regeneration_threshold"],
            "average_clarity": avg_clarity
        })

    # ---------------------- Accessor Methods ---------------------- #

    def get_summary(self):
        """Return current learning status."""
        total = len(self.feedback_data["records"])
        avg_clarity = self.feedback_data.get("average_clarity")
        threshold = self.feedback_data.get("regeneration_threshold")
        return {
            "total_cycles": total,
            "average_clarity": avg_clarity,
            "adaptive_threshold": threshold
        }


# ---------------------- Example Execution ---------------------- #

if __name__ == "__main__":
    from ai_recursive.version_diff_engine import compute_diff_summary

    # Example simulation
    integrator = FeedbackIntegrator()

    fake_diff = {
        "diff_size": 3,
        "changed_fields": ["metadata.title"],
        "added_phases": ["Phase 3"],
        "removed_phases": [],
        "modified_phases": [],
    }

    fake_eval = {"clarity_score": 8.6}

    integrator.record_cycle(fake_diff, fake_eval, regenerated=True)
    summary = integrator.get_summary()

    print("\n📚 Feedback Summary")
    print(summary)

