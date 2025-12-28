"""Budget evaluation utilities for runtime and artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from generator.hashing import hash_data


def load_budget_spec(path: Path) -> Dict[str, Any]:
    """Load a budget specification from JSON."""
    return json.loads(path.read_text(encoding="utf-8"))


def _size_bytes(path: Path) -> int | None:
    """Return size of the file in bytes, or None if missing."""
    if not path.exists():
        return None
    return path.stat().st_size


def collect_artifact_sizes(
    artifact_budgets: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Collect artifact sizes for budget evaluation."""
    results: List[Dict[str, Any]] = []
    for budget in artifact_budgets:
        paths = [Path(path) for path in budget.get("paths", [])]
        sizes = []
        missing = []
        for path in paths:
            size = _size_bytes(path)
            if size is None:
                missing.append(str(path))
            else:
                sizes.append(size)
        results.append(
            {
                "artifact_class": budget.get("artifact_class"),
                "paths": [str(path) for path in paths],
                "size_bytes": sum(sizes),
                "missing": missing,
                "max_size_mb": budget.get("max_size_mb"),
            }
        )
    return results


def evaluate_budgets(
    *,
    budget_spec: Dict[str, Any],
    phase_durations: Dict[str, float],
    artifact_sizes: List[Dict[str, Any]],
) -> Dict[str, Any]:
    # pylint: disable=too-many-locals
    """Evaluate phase duration and artifact size budgets."""
    phase_results = []
    for phase, limits in budget_spec.get("phase_budgets", {}).items():
        max_duration = float(limits.get("max_duration_sec", 0))
        observed = float(phase_durations.get(phase, 0))
        phase_results.append(
            {
                "phase": phase,
                "max_duration_sec": max_duration,
                "observed_duration_sec": observed,
                "pass": observed <= max_duration,
            }
        )

    artifact_results = []
    for entry in artifact_sizes:
        max_size_mb = float(entry.get("max_size_mb") or 0)
        size_bytes = float(entry.get("size_bytes") or 0)
        max_size_bytes = max_size_mb * 1024 * 1024
        artifact_results.append(
            {
                "artifact_class": entry.get("artifact_class"),
                "paths": entry.get("paths", []),
                "size_bytes": size_bytes,
                "max_size_bytes": max_size_bytes,
                "missing": entry.get("missing", []),
                "pass": bool(
                    entry.get("missing") == [] and size_bytes <= max_size_bytes
                ),
            }
        )

    total_duration = sum(float(duration) for duration in phase_durations.values())
    max_total = float(budget_spec.get("max_total_duration_sec", 0))
    total_pass = total_duration <= max_total

    violations = []
    for result in phase_results:
        if not result["pass"]:
            violations.append({"type": "phase_duration", "phase": result["phase"]})
    for result in artifact_results:
        if not result["pass"]:
            violations.append(
                {"type": "artifact_size", "artifact_class": result["artifact_class"]}
            )
    if not total_pass:
        violations.append({"type": "total_duration"})

    status = "pass" if not violations else "fail"
    report = {
        "status": status,
        "phase_results": phase_results,
        "artifact_results": artifact_results,
        "total_duration_sec": total_duration,
        "max_total_duration_sec": max_total,
        "violations": violations,
    }
    report["inputs_hash"] = hash_data(report)
    return report
