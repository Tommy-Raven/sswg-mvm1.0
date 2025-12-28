"""Invariant registry loading and coverage utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml

from generator.failure_emitter import ALLOWED_FAILURE_TYPES

CANONICAL_PHASES = {
    "ingest",
    "normalize",
    "parse",
    "analyze",
    "generate",
    "validate",
    "compare",
    "interpret",
    "log",
}


def load_invariants_yaml(path: Path) -> List[Dict[str, Any]]:
    """Load invariants from YAML."""
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("invariants.yaml must contain a mapping")
    invariants = payload.get("invariants", [])
    if not isinstance(invariants, list):
        raise ValueError("invariants.yaml invariants must be a list")
    return invariants


def load_registry(path: Path) -> Dict[str, Any]:
    """Load invariant registry JSON from disk."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("invariants registry must be a mapping")
    return payload


def validate_registry(payload: Dict[str, Any]) -> List[str]:
    """Validate invariant registry structure."""
    # pylint: disable=too-many-branches
    errors: List[str] = []
    anchor = payload.get("anchor")
    if not isinstance(anchor, dict):
        errors.append("missing anchor metadata")
    else:
        for key in ("anchor_id", "anchor_version", "scope", "owner", "status"):
            if not anchor.get(key):
                errors.append(f"anchor missing required field '{key}'")

    invariants = payload.get("invariants")
    if not isinstance(invariants, list):
        errors.append("invariants registry must contain an invariants list")
        return errors

    seen_ids = set()
    for index, invariant in enumerate(invariants):
        if not isinstance(invariant, dict):
            errors.append(f"invariant[{index}] must be a mapping")
            continue
        invariant_id = invariant.get("id")
        if not invariant_id:
            errors.append(f"invariant[{index}] missing id")
        elif invariant_id in seen_ids:
            errors.append(f"duplicate invariant id '{invariant_id}'")
        else:
            seen_ids.add(invariant_id)
        if not invariant.get("description"):
            errors.append(f"invariant[{index}] missing description")
        applies_to_phases = invariant.get("applies_to_phases")
        if not isinstance(applies_to_phases, list) or not applies_to_phases:
            errors.append(f"invariant[{index}] missing applies_to_phases")
        else:
            invalid_phases = sorted(
                {phase for phase in applies_to_phases if phase not in CANONICAL_PHASES}
            )
            if invalid_phases:
                errors.append(
                    f"invariant[{index}] applies_to_phases invalid phases: {invalid_phases}"
                )
        enforced_by = invariant.get("enforced_by")
        if not isinstance(enforced_by, list):
            errors.append(f"invariant[{index}] missing enforced_by list")
        failure_type = invariant.get("failure_type")
        if failure_type not in ALLOWED_FAILURE_TYPES:
            errors.append(f"invariant[{index}] invalid failure_type '{failure_type}'")
        documented_in = invariant.get("documented_in")
        if not isinstance(documented_in, list) or not documented_in:
            errors.append(f"invariant[{index}] missing documented_in list")

    return errors


def resolve_enforcement_paths(
    targets: Iterable[str], repo_root: Path
) -> List[Dict[str, Any]]:
    """Resolve enforcement targets to filesystem paths."""
    resolved: List[Dict[str, Any]] = []
    for target in targets:
        if not isinstance(target, str) or not target:
            resolved.append({"target": target, "path": None, "exists": False})
            continue
        if target.endswith(".py") or "/" in target:
            path = Path(target)
            if not path.is_absolute():
                path = repo_root / path
        else:
            path = repo_root / (target.replace(".", "/") + ".py")
        resolved.append({"target": target, "path": str(path), "exists": path.exists()})
    return resolved


def resolve_documentation_paths(
    targets: Iterable[str], repo_root: Path
) -> List[Dict[str, Any]]:
    """Resolve documentation targets to filesystem paths."""
    resolved: List[Dict[str, Any]] = []
    for target in targets:
        if not isinstance(target, str) or not target:
            resolved.append({"target": target, "path": None, "exists": False})
            continue
        path = Path(target)
        if not path.is_absolute():
            path = repo_root / path
        resolved.append({"target": target, "path": str(path), "exists": path.exists()})
    return resolved


def build_coverage_report(
    *,
    declared_invariants: Iterable[Dict[str, Any]],
    registry_payload: Dict[str, Any],
    repo_root: Path,
) -> Dict[str, Any]:
    """Build an invariant coverage report from registry metadata."""
    # pylint: disable=too-many-locals
    declared_ids = [item.get("id") for item in declared_invariants if item.get("id")]
    registry_invariants = registry_payload.get("invariants", [])
    registry_ids = [item.get("id") for item in registry_invariants if item.get("id")]

    missing_registry = sorted(set(declared_ids) - set(registry_ids))
    invariant_status = []
    enforced_ids = set()
    missing_enforcement: List[Dict[str, Any]] = []
    documentation_missing: List[Dict[str, Any]] = []

    for invariant in registry_invariants:
        invariant_id = invariant.get("id")
        enforced_by = invariant.get("enforced_by", [])
        enforcement_targets = resolve_enforcement_paths(enforced_by, repo_root)
        enforcement_ok = any(target.get("exists") for target in enforcement_targets)
        documented_in = invariant.get("documented_in", [])
        documentation_targets = resolve_documentation_paths(documented_in, repo_root)
        documentation_ok = all(target.get("exists") for target in documentation_targets)
        if enforcement_ok and invariant_id:
            enforced_ids.add(invariant_id)
        if invariant_id and not enforcement_ok:
            missing_enforcement.append(
                {
                    "id": invariant_id,
                    "enforced_by": enforced_by,
                    "enforcement_targets": enforcement_targets,
                }
            )
        if invariant_id and not documentation_ok:
            documentation_missing.append(
                {
                    "id": invariant_id,
                    "documented_in": documented_in,
                    "documentation_targets": documentation_targets,
                }
            )
        invariant_status.append(
            {
                "id": invariant_id,
                "applies_to_phases": invariant.get("applies_to_phases", []),
                "failure_type": invariant.get("failure_type"),
                "enforced_by": enforced_by,
                "enforcement_targets": enforcement_targets,
                "documented_in": documented_in,
                "documentation_targets": documentation_targets,
                "enforced": enforcement_ok,
                "documented": documentation_ok,
            }
        )

    declared_total = len(set(declared_ids))
    enforced_total = len(set(declared_ids) & enforced_ids)
    coverage_percent = 0.0
    if declared_total:
        coverage_percent = round((enforced_total / declared_total) * 100.0, 2)
    status = "pass" if not missing_registry and not missing_enforcement else "fail"

    return {
        "anchor": {
            "anchor_id": "invariant_coverage_report",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "generator.invariant_registry",
            "status": "draft",
        },
        "declared_invariants": declared_ids,
        "registry_invariants": registry_ids,
        "missing_registry": missing_registry,
        "missing_enforcement": missing_enforcement,
        "documentation_missing": documentation_missing,
        "coverage_percent": coverage_percent,
        "status": status,
        "invariant_status": invariant_status,
    }
