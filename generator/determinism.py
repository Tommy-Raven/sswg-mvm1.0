"""Determinism checks and reporting utilities."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from generator.failure_emitter import FailureLabel
from generator.hashing import hash_data


@dataclass(frozen=True)
class DeterminismReport:
    """Determinism replay results for required phases."""

    run_id: str
    inputs_hash: str
    phase_hashes: Dict[str, str]
    outputs_hash: str
    match: bool
    diff_summary: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        """Return the report as a serializable dictionary."""
        payload = {
            "anchor": {
                "anchor_id": "determinism_report",
                "anchor_version": "1.0.0",
                "scope": "run",
                "owner": "generator.determinism",
                "status": "draft",
            },
            "run_id": self.run_id,
            "inputs_hash": self.inputs_hash,
            "phase_hashes": self.phase_hashes,
            "outputs_hash": self.outputs_hash,
            "match": self.match,
            "diff_summary": self.diff_summary or {},
        }
        return payload


def _hash_phases(phase_outputs: Dict[str, Any]) -> Dict[str, str]:
    """Hash each phase output payload."""
    return {phase: hash_data(output) for phase, output in phase_outputs.items()}


def _inject_nondeterminism(
    phase_outputs: Dict[str, Any],
    target_phase: str,
) -> Dict[str, Any]:
    """Inject a nonce into a target phase to simulate nondeterminism."""
    mutated = dict(phase_outputs)
    if target_phase in mutated:
        payload = (
            dict(mutated[target_phase])
            if isinstance(mutated[target_phase], dict)
            else {}
        )
        payload["nondeterministic_nonce"] = random.randint(0, 1000000)
        mutated[target_phase] = payload
    return mutated


def replay_determinism_check(
    *,
    run_id: str,
    phase_outputs: Dict[str, Any],
    required_phases: Iterable[str],
    inject_phase: Optional[str] = None,
) -> tuple[Optional[FailureLabel], DeterminismReport]:
    """Replay deterministic phases and return a failure label on mismatch."""
    required_phases_set = set(required_phases)
    first_outputs = {phase: phase_outputs[phase] for phase in required_phases_set}
    second_outputs = first_outputs
    if inject_phase:
        second_outputs = _inject_nondeterminism(first_outputs, inject_phase)
    first_hashes = _hash_phases(first_outputs)
    second_hashes = _hash_phases(second_outputs)
    mismatch = [
        phase
        for phase in required_phases_set
        if first_hashes[phase] != second_hashes[phase]
    ]
    diff = {
        phase: {"first": first_hashes[phase], "second": second_hashes[phase]}
        for phase in mismatch
    }
    report = DeterminismReport(
        run_id=run_id,
        inputs_hash=hash_data(first_outputs),
        phase_hashes=first_hashes,
        outputs_hash=hash_data(first_hashes),
        match=not mismatch,
        diff_summary={"mismatch": mismatch, "diff": diff if mismatch else {}},
    )
    if mismatch:
        phase_id = mismatch[0]
        return (
            FailureLabel(
                Type="deterministic_failure",
                message="Deterministic replay mismatch detected",
                phase_id=phase_id,
                evidence={
                    "mismatch": mismatch,
                    "invariant_ids": ["deterministic_measurement"],
                },
            ),
            report,
        )
    return None, report


def bijectivity_check(ids: Iterable[str]) -> Optional[FailureLabel]:
    """Check identifiers for bijectivity and return a failure label."""
    seen = set()
    collisions = []
    for value in ids:
        if value in seen:
            collisions.append(value)
        seen.add(value)
    if collisions:
        return FailureLabel(
            Type="deterministic_failure",
            message="Measurement identifiers are not bijective",
            phase_id="analyze",
            evidence={
                "collisions": collisions,
                "invariant_ids": ["bijective_identifiers"],
            },
        )
    return None


def write_bijectivity_report(
    path: Path, ids: Iterable[str], failure: Optional[FailureLabel]
) -> None:
    """Write a bijectivity report payload to disk."""
    payload = {
        "anchor": {
            "anchor_id": "bijectivity_report",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "generator.determinism",
            "status": "draft",
        },
        "ids": list(ids),
        "result": "fail" if failure else "pass",
        "collisions": failure.evidence.get("collisions", []) if failure else [],
        "invariant_ids": failure.evidence.get("invariant_ids", []) if failure else [],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_determinism_report(path: Path, report: DeterminismReport) -> None:
    """Write a determinism report payload to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.as_dict(), indent=2), encoding="utf-8")
