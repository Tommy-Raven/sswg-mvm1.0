"""Phase evidence bundle utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from generator.failure_emitter import FailureLabel
from generator.hashing import hash_data


def _hash_payload(payload: Any) -> str:
    """Hash a payload for phase evidence."""
    return hash_data(payload)


def build_phase_evidence_bundle(
    *,
    run_id: str,
    pdl_obj: Dict[str, Any],
    observed_io: Dict[str, Any],
    phase_outputs: Dict[str, Any],
    invariants_registry: Dict[str, Any],
    failures_by_phase: Optional[Dict[str, FailureLabel]] = None,
) -> Dict[str, Any]:
    """Build a phase evidence bundle for a run."""
    # pylint: disable=too-many-locals
    failures_by_phase = failures_by_phase or {}
    registry_invariants = invariants_registry.get("invariants", [])

    phases = []
    for phase in pdl_obj.get("phases", []):
        phase_id = phase.get("name")
        observed = observed_io.get(phase_id, {})
        observed_inputs = observed.get("inputs", [])
        observed_outputs = observed.get("outputs", [])
        outputs_payload = phase_outputs.get(phase_id, observed_outputs)
        failure = failures_by_phase.get(phase_id)
        invariants_checked = [
            invariant.get("id")
            for invariant in registry_invariants
            if phase_id in (invariant.get("applies_to_phases") or [])
        ]
        phases.append(
            {
                "phase_id": phase_id,
                "inputs_hash": _hash_payload({"inputs": observed_inputs}),
                "outputs_hash": _hash_payload(outputs_payload),
                "invariants_checked": invariants_checked,
                "status": "fail" if failure else "pass",
                "failure_label": failure.as_dict() if failure else None,
            }
        )

    return {
        "anchor": {
            "anchor_id": "phase_evidence_bundle",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "generator.phase_evidence",
            "status": "draft",
        },
        "run_id": run_id,
        "phases": phases,
    }


def write_phase_evidence_bundle(path: Path, bundle: Dict[str, Any]) -> None:
    """Write a phase evidence bundle to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
