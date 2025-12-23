#!/usr/bin/env python3
"""
generator/main.py — SSWG Minimum Viable Model Entrypoint

AI Instructional Workflow Generator (MVM)

This version operates on schema-aligned JSON workflows:
- Loads a workflow JSON file (e.g., data/templates/campfire_workflow.json)
  or a named template slug via --template (e.g., 'campfire_basic')
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
from typing import Any, Dict, Optional, Union

import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ai_graph.dependency_mapper import DependencyGraph
from ai_validation.schema_validator import validate_workflow
from ai_visualization.mermaid_generator import mermaid_from_workflow
from ai_visualization.export_manager import export_graphviz
from ai_visualization.export_manager import export_json as viz_export_json
from ai_visualization.export_manager import export_markdown as viz_export_markdown
from ai_core.orchestrator import Orchestrator
from ai_core.workflow import Workflow
from ai_evaluation.evaluation_engine import evaluate_workflow_quality
from ai_memory.feedback_integrator import FeedbackIntegrator
from ai_recursive.version_diff_engine import compute_diff_summary
from data.data_parsing import load_template
from generator.exporters import export_json, export_markdown
from generator.history import HistoryManager
from generator.recursion_manager import RecursionManager

# ─── Logging Setup ────────────────────────────────────────────────

logger = logging.getLogger("generator.main")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)
logger.propagate = False


# ─── Optional telemetry integration ──────────────────────────────

try:
    # Import the underlying implementation, but do NOT re-export it directly.
    from ai_monitoring.structured_logger import log_event as _raw_log_event
except Exception:  # pylint: disable=broad-exception-caught
    # Fallback implementation if monitoring is not wired yet.
    def _raw_log_event(*args: Any, **kwargs: Any) -> None:  # type: ignore[unused-argument]
        """
        Very lenient fallback logger: accepts any args/kwargs.

        We try to extract an event name and payload if possible for logging,
        but otherwise just emit a generic info line.
        """
        if args:
            event = args[0]
        else:
            event = "<unknown-event>"
        payload = None
        if len(args) > 1:
            payload = args[1]
        elif "payload" in kwargs:
            payload = kwargs["payload"]
        logger.info("log_event(%s, %r)", event, payload)


def log_event(
    event: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Thin wrapper around the underlying telemetry logger.

    This gives us a stable, simple signature for the rest of the MVM code,
    regardless of how ai_monitoring.structured_logger.log_event is defined.
    """
    _raw_log_event(event, payload)


# ─── Defaults ────────────────────────────────────────────────────

# Default template path for MVM demos (used when no --template is given)
DEFAULT_TEMPLATE = Path("data/templates/campfire_workflow.json")


# ─── CLI Parsing ─────────────────────────────────────────────────

def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    """
    Parse command-line arguments for the MVM entrypoint.
    """
    parser = argparse.ArgumentParser(
        description="SSWG MVM: Workflow validation, refinement, and export.",
    )
    parser.add_argument(
        "-j",
        "--workflow-json",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help=(
            "Path to input workflow JSON (schema-aligned). "
            "Ignored if --template is provided."
        ),
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
    parser.add_argument(
        "--template",
        "-T",
        type=str,
        help=(
            "Optional template workflow slug to start from "
            "(e.g. 'campfire_basic' → data/templates/campfire_basic.json)."
        ),
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the canonical demo pipeline end-to-end using the campfire template.",
    )

    return parser.parse_args(argv)


# ─── IO Helpers ──────────────────────────────────────────────────

def load_workflow(path: Path) -> Dict[str, Any]:
    """
    Load a workflow JSON file from disk.
    """
    if not path.exists():
        raise FileNotFoundError(f"Workflow JSON not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    logger.info(
        "Loaded workflow %s from %s", data.get("workflow_id", "<unknown>"), path
    )
    return data


# ─── Core Processing Pipeline ────────────────────────────────────

def process_workflow(
    workflow: Dict[str, Any],
    *,
    enable_refinement: bool = True,
    out_dir: Path = Path("data/outputs"),
) -> Dict[str, Any]:
    """
    Run the MVM pipeline on a workflow dict in the canonical order:
    - schema validation
    - dependency graph autocorrect
    - evaluation + semantic deltas
    - recursive refinement with llm_adapter
    - visualization exports
    """
    workflow_id = workflow.get("workflow_id", "unnamed_workflow")
    log_event("mvm.process.started", {"workflow_id": workflow_id})

    orchestrator = Orchestrator()
    workflow_obj = Workflow(workflow)
    orchestrator.telemetry.record("loaded_via_orchestrator", {"workflow_id": workflow_obj.id})

    # 1. Schema validation
    ok, errors = validate_workflow(workflow)
    if not ok and errors:
        logger.warning("Initial schema validation reported %d issues.", len(errors))
        workflow.setdefault("evaluation", {}).setdefault(
            "notes",
            [],
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
                "Unresolved dependency cycle detected; manual review required.",
            )

    # 3. Generate mermaid representation (for logging/debugging)
    mermaid = mermaid_from_workflow(workflow)
    logger.info("Mermaid graph for workflow %s:\n%s", workflow_id, mermaid)

    # 4. Evaluation + semantic scoring
    base_quality = evaluate_workflow_quality(workflow)
    workflow.setdefault("evaluation", {})["quality"] = base_quality

    # 5. Recursive refinement (single iteration) if enabled
    refined = deepcopy(workflow)
    if enable_refinement:
        recursion_manager = RecursionManager(output_dir=out_dir)
        outcome = recursion_manager.run_cycle(refined, depth=0)
        refined = outcome.refined_workflow
        refined.setdefault("evaluation", {}).update(
            {
                "before": outcome.before_report.get("quality"),
                "after": outcome.after_report.get("quality"),
                "semantic_delta": outcome.semantic_delta,
                "score_delta": outcome.score_delta,
                "plot": str(outcome.plot_path),
            }
        )
        log_event(
            "mvm.process.refined",
            {
                "workflow_id": refined.get("workflow_id", workflow_id),
                "score_delta": outcome.score_delta,
                "semantic_delta": outcome.semantic_delta,
            },
        )

    # 6. Export updated visualization assets
    export_graphviz(refined, str(out_dir))
    viz_export_json(refined, str(out_dir))
    viz_export_markdown(refined, str(out_dir))

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


def record_feedback(original: Dict[str, Any], refined: Dict[str, Any]) -> None:
    """Record diff-driven feedback into persistent memory."""

    diff_summary = compute_diff_summary(original, refined)
    clarity_after = (
        refined.get("evaluation", {})
        .get("after", {})
        .get("metrics", {})
        .get("clarity", 0.0)
    )
    FeedbackIntegrator().record_cycle(
        diff_summary,
        {"clarity_score": clarity_after},
        regenerated=True,
    )


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

    modifications: list[str] = []
    if len(refined.get("modules", [])) != len(original.get("modules", [])):
        modifications.append("Module count changed")
    if new_score != orig_score:
        modifications.append(f"Composite score changed ({orig_score} -> {new_score})")
    if not modifications:
        # No detectable differences worth a history record
        return

    hm = HistoryManager()
    record = hm.record_transition(
        parent_workflow_id=parent_id,
        child_workflow_id=child_id,
        modifications=modifications,
        score_delta=score_delta,
    )
    logger.info(
        "Recorded history: %s -> %s (Δ score=%.3f)",
        record.parent_workflow,
        record.child_workflow,
        record.score_delta,
    )


# ─── Public API Entry for Programmatic Use ───────────────────────

def run_mvm(
    workflow_source: Union[Path, Dict[str, Any]],
    *,
    out_dir: Path = Path("data/outputs"),
    enable_refinement: bool = True,
    enable_history: bool = True,
    preview: bool = False,
) -> Dict[str, Any]:
    """
    Public function to run the MVM pipeline on a workflow.

    Args:
        workflow_source:
            Either a Path to a JSON file, or an already-loaded workflow dict.

    Returns:
        The refined workflow dict.
    """
    if isinstance(workflow_source, Path):
        workflow = load_workflow(workflow_source)
    else:
        # Defensive copy so callers can reuse their original dict
        workflow = deepcopy(workflow_source)

    original = deepcopy(workflow)
    refined = process_workflow(
        workflow,
        enable_refinement=enable_refinement,
        out_dir=out_dir,
    )
    export_artifacts(refined, out_dir)
    record_history_if_needed(original, refined, enable_history=enable_history)
    record_feedback(original, refined)

    if preview:
        snippet = json.dumps(refined, indent=2)[:800]
        print("\n--- Workflow Preview ---\n", snippet, "...\n")

    return refined


# ─── Main CLI Entrypoint ─────────────────────────────────────────

def main(argv: Optional[list] = None) -> int:
    """
    Command-line entrypoint for the SSWG MVM generator.
    """
    args = parse_args(argv)

    if args.version:
        print("SSWG Workflow Generator — MVM v0.1.0")
        return 0

    # Resolve workflow source:
    # - --demo forces the canonical template + output dir
    # - If --template is provided, load from data/templates/<slug>.json
    # - Otherwise, use the path from --workflow-json
    out_dir = args.out_dir
    if args.demo:
        workflow_source = DEFAULT_TEMPLATE
        out_dir = Path("data/outputs/demo_run")
        logger.info("Demo mode: using template %s", workflow_source)
    elif args.template:
        try:
            workflow_source = load_template(args.template)
            logger.info(
                "Loaded workflow from template slug '%s' via data.templates",
                args.template,
            )
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Failed to load template '%s'", args.template)
            return 1
    else:
        workflow_source = args.workflow_json

    try:
        refined = run_mvm(
            workflow_source,
            out_dir=out_dir,
            enable_refinement=not args.no_refine,
            enable_history=not args.no_history,
            preview=args.preview,
        )
        logger.info(
            "MVM run completed for workflow_id=%s",
            refined.get("workflow_id", "<unknown>"),
        )
        return 0
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("MVM run failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
