#!/usr/bin/env python3
"""
ai_monitoring/cli_dashboard.py — Minimal CLI dashboard for SSWG MVM.

Responsibilities (MVM):
- Track workflow "cycles" (runs) with success/failure counts.
- Track per-phase success/failure counts.
- Render a short human-readable summary at the end of orchestration.

This module is intentionally lightweight and suitable for local / dev use.
In headless environments, callers may swap this out for a no-op stub.
"""

from __future__ import annotations

import time
from typing import Dict

from .structured_logger import log_event


class CLIDashboard:
    def __init__(self) -> None:
        self.start_time = time.time()
        self.cycles = 0
        self.success = 0
        self.failures = 0

        # Per-phase stats: phase_id -> {"success": int, "failures": int}
        self.phase_stats: Dict[str, Dict[str, int]] = {}

    # ------------------------------------------------------------------ #
    # Cycle-level tracking
    # ------------------------------------------------------------------ #
    def record_cycle(self, success: bool = True) -> None:
        """
        Record a single workflow cycle outcome.
        """
        self.cycles += 1
        if success:
            self.success += 1
        else:
            self.failures += 1

        log_event(
            "dashboard.cycle",
            {
                "success": success,
                "cycles": self.cycles,
                "success_count": self.success,
                "failure_count": self.failures,
            },
        )

    # ------------------------------------------------------------------ #
    # Phase-level tracking
    # ------------------------------------------------------------------ #
    def record_phase(self, phase_id: str, success: bool = True) -> None:
        """
        Record the outcome of executing a single phase.
        """
        stats = self.phase_stats.setdefault(phase_id, {"success": 0, "failures": 0})

        if success:
            stats["success"] += 1
        else:
            stats["failures"] += 1

        log_event(
            "dashboard.phase",
            {
                "phase": phase_id,
                "success": success,
                "success_count": stats["success"],
                "failure_count": stats["failures"],
            },
        )

    # ------------------------------------------------------------------ #
    # Rendering
    # ------------------------------------------------------------------ #
    def render(self) -> None:
        """
        Render a summary of cycles and phase statistics to stdout.
        """
        elapsed = time.time() - self.start_time
        success_rate = (self.success / max(1, self.cycles)) * 100.0

        log_event("dashboard.render.start", {"elapsed_s": elapsed})

        print("----- CLI DASHBOARD -----")
        print(f"Elapsed Time: {elapsed:.2f}s")
        print(f"Total Cycles: {self.cycles}")
        print(f"Successful:  {self.success}")
        print(f"Failed:      {self.failures}")
        print(f"Success Rate: {success_rate:.1f}%")

        if self.phase_stats:
            print("\nPer-Phase Stats:")
            for phase_id, stats in self.phase_stats.items():
                total = stats["success"] + stats["failures"]
                rate = (stats["success"] / max(1, total)) * 100.0
                print(
                    f"  - {phase_id}: "
                    f"{stats['success']}/{total} ok "
                    f"({rate:.1f}% success)"
                )

        print("--------------------------")

        log_event(
            "dashboard.render.end",
            {
                "elapsed_s": elapsed,
                "cycles": self.cycles,
                "success": self.success,
                "failures": self.failures,
            },
        )


# End of ai_monitoring/cli_dashboard.py
