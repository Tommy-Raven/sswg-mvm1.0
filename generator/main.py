#!/usr/bin/env python3
"""
generator/main.py — SSWG Minimum Viable Model Entrypoint

AI Instructional Workflow Generator (MVM)

This version operates on schema-aligned JSON workflows:
- Loads a workflow JSON file (e.g., data/templates/campfire_workflow.json)
- Validates it against workflow_schema.json
- Builds and checks a dependency graph, with autocorrect for common issues
- Performs a simple recursive refinement pass
- Exports JSON + Markdown artifacts
- Records history of parent/child workflow relationships
"""

from __future__ import annotations

import argparse
import json
import logging
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

# ─── Logging Setup ────────────────────────────────────────────────
logger = logging.getLogger("generator.main")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)

# ─── Imports from other subsystems ───────────────────────────────
from ai_validation.schema_validator import validate_workflow
from ai_graph.dependency_mapper import DependencyGraph
from ai_visualization.mermaid_generator import mermaid_from_workflow
from generator.recursion_manager import simple_refiner
from generator.exporters import export_json, export_markdown
from generator.history import HistoryManager

# Optional telemetry integration
try:
    from ai_monitoring.structured_logger import log_event
except Exception:  # fallback if monitoring not wired yet
    def log_event(event: str, payload: Optional[dict] = None) -> None:
        logger.info("log_event(%s, %r)", event, payload)


# Default template path for MVM demos
DEFAULT_TEMPLATE = Path("data/templates/campfire_workflow.json")


# ─── CLI Parsing ─────────────────────────────────────────────────
def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SSWG MVM: Workflow validation, refinement, and export."
    )
    parser.add_argument(
        "-j",
        "--workflow-json",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help="Path to input workflow JSON (schema-aligned).",
    )
    parser.add_argument(
        "-o",
        "--out-dir",
        type=Path,
        default=Path("data/outputs"),
        help="Directory for exported artifacts.",
    )
    parser.add_argument(
        "--no-refine",
        action="store_true",
        help="Disable recursive refinement step.",
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="Disable history recording.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Print a JSON preview of the final workflow.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print generator version and exit.",
    )
    return parser.parse_args(argv)


# ─── IO Helpers ──────────────────────────────────────────────────
def load_workflow(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Workflow JSON not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    logger.info("Loaded workflow %s from %s", data.get("workflow_id", "<unknown>"), path)
    return data


# ─── Core Processing Pipeline ────────────────────────────────────
def process_workflow(
    workflow: Dict[str, Any],
    *,
    enable_refinement: bool = True,
) -> Dict[str, Any]:
    """
    Run the MVM pipeline on a workflow dict:
    - schema validation
    - dependency graph autocorrect
    - mermaid visualization
    - simple refinement (optional)
    """
    workflow_id = workflow.get("workflow_id", "unnamed_workflow")
    log_event("mvm.process.started", {"workflow_id": workflow_id})

    # 1. Schema validation
    ok, errors = validate_workflow(workflow)
    if not ok and errors:
        logger.warning("Initial schema validation reported %d issues.", len(errors))
        workflow.setdefault("evaluation", {}).setdefault(
            "notes", []
        ).append("Schema validation reported issues; see logs for details.")

    # 2. Build dependency graph and autocorrect structural issues
    modules = workflow.get("modules", [])
    dg = DependencyGraph(modules)
    dg.autocorrect_missing_dependencies()

    if dg.detect_cycle():
        logger.warning("Dependency cycle detected; attempting autocorrect.")
        corrected = dg.attempt_autocorrect_cycle()
        if not corrected and workflow.get("evaluation") is not None:
            workflow["evaluation"].setdefault("notes", []).append(
                "Unresolved dependency cycle detected; manual review required."
            )

    # 3. Generate mermaid representation (for logging/debugging)
    mermaid = mermaid_from_workflow(workflow)
    logger.info("Mermaid graph for workflow %s:\n%s", workflow_id, mermaid)

    # 4. Simple refinement (single iteration) if enabled
    refined = deepcopy(workflow)
    if enable_refinement:
        refined = simple_refiner(refined)
        log_event(
            "mvm.process.refined",
            {"workflow_id": refined.get("workflow_id", workflow_id)},
        )

    log_event("mvm.process.completed", {"workflow_id": workflow_id})
    return refined


# ─── Export & History Recording ──────────────────────────────────
def export_artifacts(
    workflow: Dict[str, Any],
    out_dir: Path,
) -> Dict[str, str]:
    """
    Export JSON + Markdown artifacts for the workflow.

    Returns:
        Mapping from artifact type to path (as str).
    """
    out_dir = out_dir or Path("data/outputs")
    out_dir_str = str(out_dir)
    logger.info("Exporting artifacts to %s", out_dir_str)

    json_path = export_json(workflow, out_dir_str)
    md_path = export_markdown(workflow, out_dir_str)

    return {"json": json_path, "markdown": md_path}


def record_history_if_needed(
    original: Dict[str, Any],
    refined: Dict[str, Any],
    *,
    enable_history: bool = True,
) -> None:
    """
    Record a lineage entry if there is a meaningful difference between
    original and refined workflows (e.g., coverage improvement, added modules).
    """
    if not enable_history:
        return

    parent_id = original.get("workflow_id", "unnamed_workflow")
    child_id = refined.get("workflow_id", parent_id)

    # Use evaluation composite or coverage delta if available
    orig_eval = original.get("evaluation", {}) or {}
    new_eval = refined.get("evaluation", {}) or {}

    orig_score = float(orig_eval.get("composite_score", 0.0) or 0.0)
    new_score = float(new_eval.get("composite_score", 0.0) or 0.0)
    score_delta = new_score - orig_score

    modifications = []
    if len(refined.get("modules", [])) != len(original.get("modules", [])):
        modifications.append("Module count changed")
    if new_score != orig_score:
        modifications.append(f"Composite score changed ({orig_score} -> {new_score})")
    if not modifications:
        # No detectable differences worth a history record
        return

    hm = HistoryManager()
    record = hm.record_transition(
        parent_workflow=parent_id,
        child_workflow=child_id,
        modifications=modifications,
        score_delta=score_delta,
        metadata={"original_eval": orig_eval, "refined_eval": new_eval},
    )
    logger.info(
        "Recorded history: %s -> %s (Δscore=%.3f)",
        record.parent_workflow,
        record.child_workflow,
        record.score_delta,
    )


# ─── Public API Entry for Programmatic Use ───────────────────────
def run_mvm(
    workflow_path: Path,
    *,
    out_dir: Path = Path("data/outputs"),
    enable_refinement: bool = True,
    enable_history: bool = True,
    preview: bool = False,
) -> Dict[str, Any]:
    """
    Public function to run the MVM pipeline on a workflow JSON file.

    Returns:
        The refined workflow dict.
    """
    workflow = load_workflow(workflow_path)
    original = deepcopy(workflow)
    refined = process_workflow(workflow, enable_refinement=enable_refinement)
    export_artifacts(refined, out_dir)
    record_history_if_needed(original, refined, enable_history=enable_history)

    if preview:
        snippet = json.dumps(refined, indent=2)[:800]
        print("\n--- Workflow Preview ---\n", snippet, "...\n")

    return refined


# ─── Main CLI Entrypoint ─────────────────────────────────────────
def main(argv: Optional[list] = None) -> int:
    args = parse_args(argv)

    if args.version:
        print("SSWG Workflow Generator — MVM v0.1.0")
        return 0

    try:
        refined = run_mvm(
            workflow_path=args.workflow_json,
            out_dir=args.out_dir,
            enable_refinement=not args.no_refine,
            enable_history=not args.no_history,
            preview=args.preview,
        )
        logger.info(
            "MVM run completed for workflow_id=%s",
            refined.get("workflow_id", "<unknown>"),
        )
        return 0
    except Exception as e:
        logger.error("MVM run failed: %s", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
# End of generator/main.py