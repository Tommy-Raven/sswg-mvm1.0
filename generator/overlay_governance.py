"""Overlay governance validation helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft202012Validator, RefResolver


def _load_schema(schema_path: Path) -> Dict[str, Any]:
    """Load a JSON schema from disk."""
    return json.loads(schema_path.read_text(encoding="utf-8"))


def get_overlay_validator(schema_dir: Path) -> Draft202012Validator:
    """Return a validator for overlay descriptors."""
    schema = _load_schema(schema_dir / "overlay-descriptor.json")
    base_uri = schema_dir.as_uri().rstrip("/") + "/"
    resolver = RefResolver(base_uri=base_uri, referrer=schema)
    return Draft202012Validator(schema, resolver=resolver)


def validate_overlay_descriptor(
    overlay: Dict[str, Any],
    *,
    schema_dir: Path,
    overlay_path: Path | None = None,
) -> List[Dict[str, Any]]:
    """Validate an overlay descriptor and return lint results."""
    validator = get_overlay_validator(schema_dir)
    errors = sorted(validator.iter_errors(overlay), key=lambda e: e.path)
    results: List[Dict[str, Any]] = [
        {
            "message": error.message,
            "path": list(error.path),
            "schema_path": list(error.schema_path),
            "overlay_path": str(overlay_path) if overlay_path else None,
        }
        for error in errors
    ]

    operations = overlay.get("operations", [])
    paths = [op.get("path") for op in operations if op.get("path")]
    if len(paths) != len(set(paths)):
        results.append(
            {
                "message": "Overlay contains duplicate operation paths, ambiguous interpretation.",
                "path": ["operations"],
                "schema_path": [],
                "overlay_path": str(overlay_path) if overlay_path else None,
            }
        )

    precedence = overlay.get("precedence", {})
    scope = precedence.get("scope", "")
    notes = precedence.get("notes", "")
    rules = precedence.get("rules", "")
    if not scope:
        results.append(
            {
                "message": "Overlay precedence scope must be provided.",
                "path": ["precedence", "scope"],
                "schema_path": [],
                "overlay_path": str(overlay_path) if overlay_path else None,
            }
        )
    if not rules:
        results.append(
            {
                "message": "Overlay precedence rules must be provided.",
                "path": ["precedence", "rules"],
                "schema_path": [],
                "overlay_path": str(overlay_path) if overlay_path else None,
            }
        )
    if scope == "global" and "explicit" not in notes.lower():
        results.append(
            {
                "message": "Global overlay scope requires explicit precedence notes.",
                "path": ["precedence", "notes"],
                "schema_path": [],
                "overlay_path": str(overlay_path) if overlay_path else None,
            }
        )

    compatibility = overlay.get("compatibility", {})
    if compatibility.get("compatibility") == "breaking":
        migration_plan = compatibility.get("migration_plan_ref")
        rollback_plan = compatibility.get("rollback_plan_ref")
        if not migration_plan:
            results.append(
                {
                    "message": "Breaking overlays require a migration plan artifact path.",
                    "path": ["compatibility", "migration_plan_ref"],
                    "schema_path": [],
                    "overlay_path": str(overlay_path) if overlay_path else None,
                }
            )
        if not rollback_plan:
            results.append(
                {
                    "message": "Breaking overlays require a rollback plan artifact path.",
                    "path": ["compatibility", "rollback_plan_ref"],
                    "schema_path": [],
                    "overlay_path": str(overlay_path) if overlay_path else None,
                }
            )
        if migration_plan and not Path(migration_plan).exists():
            results.append(
                {
                    "message": "Migration plan artifact path does not exist.",
                    "path": ["compatibility", "migration_plan_ref"],
                    "schema_path": [],
                    "overlay_path": str(overlay_path) if overlay_path else None,
                }
            )
        if rollback_plan and not Path(rollback_plan).exists():
            results.append(
                {
                    "message": "Rollback plan artifact path does not exist.",
                    "path": ["compatibility", "rollback_plan_ref"],
                    "schema_path": [],
                    "overlay_path": str(overlay_path) if overlay_path else None,
                }
            )

    return results


def detect_overlay_ambiguity(overlays: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect ambiguous override ordering in overlays."""
    errors: List[Dict[str, Any]] = []
    scope_path_map: Dict[tuple[str, str], List[Dict[str, Any]]] = {}

    for overlay in overlays:
        overlay_id = overlay.get("overlay_id", "unknown")
        precedence = overlay.get("precedence", {})
        scope = precedence.get("scope", "")
        order = precedence.get("order")
        for operation in overlay.get("operations", []):
            if operation.get("op") != "override":
                continue
            path = operation.get("path")
            if not path:
                continue
            key = (scope, path)
            scope_path_map.setdefault(key, []).append(
                {"overlay_id": overlay_id, "order": order}
            )

    for (scope, path), entries in scope_path_map.items():
        if len(entries) <= 1:
            continue
        orders = [entry.get("order") for entry in entries]
        if any(order is None for order in orders) or len(set(orders)) != len(orders):
            errors.append(
                {
                    "message": "Ambiguous override ordering detected for overlay precedence.",
                    "scope": scope,
                    "path": path,
                    "overlay_ids": [entry["overlay_id"] for entry in entries],
                }
            )

    return errors


def build_overlay_promotion_report(
    overlays: List[Dict[str, Any]],
    *,
    lint_errors: Dict[str, List[Dict[str, Any]]],
    ambiguity_errors: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build a promotion report for overlay descriptors."""
    ambiguity_map: Dict[str, List[Dict[str, Any]]] = {}
    for error in ambiguity_errors:
        for overlay_id in error.get("overlay_ids", []):
            ambiguity_map.setdefault(overlay_id, []).append(error)

    overlay_reports = []
    for overlay in overlays:
        overlay_id = overlay.get("overlay_id", "unknown")
        compatibility = overlay.get("compatibility", {})
        migration_present = compatibility.get("compatibility") != "breaking" or all(
            compatibility.get(key)
            for key in ("migration_plan_ref", "rollback_plan_ref")
        )
        overlay_reports.append(
            {
                "overlay_id": overlay_id,
                "overlay_version": overlay.get("overlay_version", ""),
                "scope": overlay.get("precedence", {}).get("scope", ""),
                "compat": compatibility.get("compatibility", ""),
                "migration_present": migration_present,
                "lint_pass": not lint_errors.get(overlay_id, []),
                "ambiguity_pass": not ambiguity_map.get(overlay_id, []),
            }
        )

    return {
        "anchor": {
            "anchor_id": "overlay_promotion_report",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "generator.overlay_governance",
            "status": "draft",
        },
        "overlays": overlay_reports,
    }
