#!/usr/bin/env python3
"""
ai_validation/version_migrator.py — Workflow version migration for SSWG MVM.

Goal:
- Provide a simple, explicit pattern for migrating workflow artifacts between
  schema / model versions.

MVM behavior:
- Maintains a registry of migration functions keyed by (from_version, to_version).
- Exposes helpers:
    - register_migration
    - migrate_to_version
    - migrate_to_latest
- If no migration path is registered, returns the input workflow unchanged
  and annotates it with a note in workflow["evaluation"]["notes"].

This is intentionally conservative and deterministic. Real migrations can be
added incrementally as the schema evolves.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Tuple

logger = logging.getLogger("ai_validation.version_migrator")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)

MigrationFunc = Callable[[Dict[str, Any]], Dict[str, Any]]

# (from_version, to_version) -> migration_function
_MIGRATIONS: Dict[Tuple[str, str], MigrationFunc] = {}

try:
    # Optional: current version hint from meta_knowledge_repo
    from meta_knowledge_repo.versioning import get_current_version
except Exception:  # fallback if not wired yet

    def get_current_version() -> str:  # type: ignore[no-redef]
        return "0.0.0-MVM"


# --------------------------------------------------------------------------- #
# Registration API
# --------------------------------------------------------------------------- #
def register_migration(from_version: str, to_version: str, func: MigrationFunc) -> None:
    """
    Register a migration function from one version to another.

    Args:
        from_version: e.g. "1.0.0"
        to_version:   e.g. "1.1.0"
        func:         function that takes a workflow dict and returns a migrated dict
    """
    key = (from_version, to_version)
    if key in _MIGRATIONS:
        logger.warning(
            "Overwriting existing migration %s -> %s", from_version, to_version
        )
    _MIGRATIONS[key] = func
    logger.info("Registered migration %s -> %s", from_version, to_version)


def list_migrations() -> List[Tuple[str, str]]:
    """
    List all registered (from_version, to_version) pairs.
    """
    return sorted(_MIGRATIONS.keys())


# --------------------------------------------------------------------------- #
# Migration logic
# --------------------------------------------------------------------------- #
def _find_direct_migration(from_version: str, to_version: str) -> MigrationFunc | None:
    return _MIGRATIONS.get((from_version, to_version))


def _annotate_no_migration(
    workflow: Dict[str, Any], target_version: str
) -> Dict[str, Any]:
    """
    If no migration path exists, return workflow unchanged but annotate.
    """
    evaluation = workflow.setdefault("evaluation", {})
    notes = evaluation.setdefault("notes", [])
    notes.append(
        f"Version migrator: no migration path found from {workflow.get('version', 'unknown')} "
        f"to {target_version}; workflow used as-is."
    )
    logger.warning(
        "No migration path found from %s to %s; returning workflow unchanged.",
        workflow.get("version", "unknown"),
        target_version,
    )
    return workflow


def migrate_to_version(
    workflow: Dict[str, Any],
    target_version: str,
) -> Dict[str, Any]:
    """
    Migrate a workflow dict to the target version, if possible.

    Strategy (MVM):
    - If workflow.version == target_version: return as is.
    - If a direct migration (version -> target_version) exists, apply it.
    - Otherwise, return the workflow unchanged and annotate evaluation.notes.

    Later, this can be extended to walk multi-hop chains (1.0 -> 1.1 -> 2.0).
    """
    current_version = str(workflow.get("version", "0.0.0"))

    if current_version == target_version:
        logger.info("Workflow already at target version %s", target_version)
        return workflow

    logger.info("Attempting migration %s -> %s", current_version, target_version)
    direct = _find_direct_migration(current_version, target_version)
    if not direct:
        return _annotate_no_migration(workflow, target_version)

    migrated = direct(workflow)
    migrated["version"] = target_version
    logger.info("Migration %s -> %s completed.", current_version, target_version)
    return migrated


def migrate_to_latest(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate workflow to the latest known version according to get_current_version().

    If no path exists, returns the workflow unchanged but annotated.
    """
    latest = get_current_version()
    return migrate_to_version(workflow, latest)


# --------------------------------------------------------------------------- #
# Example no-op migration pattern (commented, for future reference)
# --------------------------------------------------------------------------- #
# def _noop_migration_example(wf: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Template for a migration that just renames keys or adds missing defaults.
#     """
#     wf = dict(wf)  # shallow copy or use copy.deepcopy in more complex cases
#     # Example: ensure evaluation has a composite_score field
#     eval_block = wf.setdefault("evaluation", {})
#     eval_block.setdefault("composite_score", 0.0)
#     return wf
#
# register_migration("1.0.0", "1.1.0", _noop_migration_example)


if __name__ == "__main__":
    # Minimal self-test: calling migrate_to_latest on a bare workflow
    wf = {"workflow_id": "wf_demo", "version": "0.0.0"}
    migrated = migrate_to_latest(wf)
    print("Original:", wf)
    print("Migrated:", migrated)
