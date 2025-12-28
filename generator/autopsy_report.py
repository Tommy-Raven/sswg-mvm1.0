"""Autopsy report utilities for failure diagnostics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from generator.failure_emitter import FailureLabel


def _extract_invariant_ids(evidence: Dict[str, Any]) -> List[str]:
    """Extract invariant identifiers from failure evidence."""
    invariant_ids: List[str] = []
    if not evidence:
        return invariant_ids
    if isinstance(evidence.get("invariant_id"), str):
        invariant_ids.append(evidence["invariant_id"])
    if isinstance(evidence.get("invariant_ids"), list):
        invariant_ids.extend(
            [
                item
                for item in evidence.get("invariant_ids", [])
                if isinstance(item, str)
            ]
        )
    return sorted(set(invariant_ids))


def build_autopsy_report(
    *,
    run_id: str,
    failure: FailureLabel,
    invariants_registry: Dict[str, Any],
) -> Dict[str, Any]:
    """Build an autopsy report payload from a failure label."""
    registry_invariants = {
        invariant.get("id"): invariant
        for invariant in invariants_registry.get("invariants", [])
        if isinstance(invariant, dict)
    }
    invariant_ids = _extract_invariant_ids(failure.evidence or {})
    violated_invariants = [
        {
            "id": invariant_id,
            "description": registry_invariants.get(invariant_id, {}).get("description"),
            "failure_type": registry_invariants.get(invariant_id, {}).get(
                "failure_type"
            ),
        }
        for invariant_id in invariant_ids
    ]

    return {
        "anchor": {
            "anchor_id": "autopsy_report",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "generator.autopsy_report",
            "status": "draft",
        },
        "run_id": run_id,
        "failure_label": failure.as_dict(),
        "violated_invariant_ids": invariant_ids,
        "violated_invariants": violated_invariants,
    }


def write_autopsy_report(path: Path, report: Dict[str, Any]) -> None:
    """Write an autopsy report to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
