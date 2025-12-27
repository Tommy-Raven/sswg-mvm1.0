from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from generator.failure_emitter import FailureLabel


def load_pdl(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("PDL YAML must parse to a mapping object")
    return data


def build_phase_io_manifest(
    pdl_obj: Dict[str, Any],
    observed: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    observed = observed or {}
    phases = []
    for phase in pdl_obj.get("phases", []):
        phase_id = phase["name"]
        observed_entry = observed.get(phase_id, {})
        phases.append(
            {
                "phase_id": phase_id,
                "declared_inputs": [item["id"] for item in phase.get("inputs", [])],
                "declared_outputs": [item["id"] for item in phase.get("outputs", [])],
                "observed_inputs": observed_entry.get("inputs", []),
                "observed_outputs": observed_entry.get("outputs", []),
                "observed_actions": observed_entry.get("actions", []),
            }
        )
    return {
        "anchor": {
            "anchor_id": "phase_io_manifest",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "generator.phase_io",
            "status": "draft",
        },
        "phases": phases,
    }


def detect_phase_collapse(manifest: Dict[str, Any], pdl_obj: Dict[str, Any]) -> Optional[FailureLabel]:
    constraints_by_phase = {
        phase["name"]: phase.get("constraints", {}) for phase in pdl_obj.get("phases", [])
    }
    for phase_entry in manifest.get("phases", []):
        phase_id = phase_entry["phase_id"]
        declared_outputs = set(phase_entry.get("declared_outputs", []))
        observed_outputs = set(phase_entry.get("observed_outputs", []))
        undeclared_outputs = sorted(observed_outputs - declared_outputs)
        if undeclared_outputs:
            return FailureLabel(
                Type="schema_failure",
                message="Phase produced undeclared outputs",
                phase_id=phase_id,
                evidence={"undeclared_outputs": undeclared_outputs},
            )
        constraints = constraints_by_phase.get(phase_id, {})
        if constraints.get("no_generation") and "generate" in phase_entry.get("observed_actions", []):
            return FailureLabel(
                Type="schema_failure",
                message="Phase performed disallowed generation action",
                phase_id=phase_id,
                evidence={"action": "generate"},
            )
    return None


def write_manifest(path: Path, manifest: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
