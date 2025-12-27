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
from datetime import datetime, timezone
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
from ai_core.orchestrator import Orchestrator, RunContext
from ai_core.workflow import Workflow
from ai_evaluation.checkpoints import EvaluationCheckpointer
from ai_evaluation.evaluation_engine import evaluate_workflow_quality
from ai_memory.memory_store import MemoryStore
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


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _snapshot_dependencies(modules: list[dict[str, Any]]) -> dict[str, list[str]]:
    snapshot: dict[str, list[str]] = {}
    for module in modules:
        module_id = module.get("module_id")
        if not module_id:
            continue
        deps = [str(dep) for dep in (module.get("dependencies", []) or [])]
        snapshot[str(module_id)] = deps
    return snapshot


def _build_dependency_graph(modules: list[dict[str, Any]]) -> dict[str, list[list[str]]]:
    nodes = sorted(
        {
            str(module.get("module_id"))
            for module in modules
            if module.get("module_id")
        }
    )
    edges: list[list[str]] = []
    for module in modules:
        module_id = module.get("module_id")
        if not module_id:
            continue
        for dep in module.get("dependencies", []) or []:
            edges.append([str(dep), str(module_id)])
    return {"nodes": nodes, "edges": edges}


def _build_dependency_index(
    modules: list[dict[str, Any]],
) -> dict[str, dict[str, list[str]]]:
    module_ids = {
        str(module.get("module_id"))
        for module in modules
        if module.get("module_id")
    }
    upstream: dict[str, list[str]] = {}
    downstream: dict[str, list[str]] = {module_id: [] for module_id in module_ids}
    missing: dict[str, list[str]] = {}

    for module in modules:
        module_id = module.get("module_id")
        if not module_id:
            continue
        deps = [str(dep) for dep in (module.get("dependencies", []) or [])]
        known = sorted([dep for dep in deps if dep in module_ids])
        missing_deps = sorted([dep for dep in deps if dep not in module_ids])
        upstream[str(module_id)] = known
        if missing_deps:
            missing[str(module_id)] = missing_deps
        for dep in known:
            downstream.setdefault(dep, []).append(str(module_id))

    downstream = {key: sorted(value) for key, value in downstream.items()}
    payload = {"upstream": upstream, "downstream": downstream}
    if missing:
        payload["missing"] = missing
    return payload


def _append_causal_entry(workflow: Dict[str, Any], entry: Dict[str, Any]) -> None:
    ledger = workflow.setdefault("causal_ledger", [])
    if isinstance(ledger, list):
        ledger.append(entry)


def _normalize_task_packaging(task: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
    updated = False
    normalized = dict(task)
    task_id = normalized.get("task_id") or normalized.get("id")
    task_ref = normalized.get("task_ref")

    if task_id and "task_id" not in normalized:
        normalized["task_id"] = task_id
        updated = True

    if task_ref:
        reuse = dict(normalized.get("reuse", {}))
        if not reuse.get("mode"):
            reuse["mode"] = "reference"
        normalized["reuse"] = reuse
        updated = True
        return updated, normalized

    if not task_id:
        raise ValueError("Task is missing a stable id or task_ref.")

    if not normalized.get("description") and normalized.get("action"):
        normalized["description"] = f"Execute action: {normalized['action']}"
        updated = True
    if not normalized.get("description") and not normalized.get("action"):
        raise ValueError(f"Task {task_id} is missing a description or action.")

    prerequisites = normalized.get("prerequisites")
    if prerequisites is None and normalized.get("inputs") is not None:
        normalized["prerequisites"] = list(normalized.get("inputs") or [])
        updated = True

    expected_outputs = normalized.get("expected_outputs")
    if expected_outputs is None and normalized.get("outputs") is not None:
        normalized["expected_outputs"] = list(normalized.get("outputs") or [])
        updated = True

    if normalized.get("prerequisites") is None:
        raise ValueError(f"Task {task_id} is missing prerequisites.")
    if normalized.get("expected_outputs") is None:
        raise ValueError(f"Task {task_id} is missing expected_outputs.")

    reuse = dict(normalized.get("reuse", {}))
    if reuse.get("mode") == "copy" and not reuse.get("justification"):
        raise ValueError(f"Task {task_id} copy reuse requires justification.")
    if reuse:
        normalized["reuse"] = reuse

    return updated, normalized


def _apply_task_packaging(
    workflow: Dict[str, Any],
    *,
    change_source: str,
) -> None:
    phases = workflow.get("phases", []) or []
    changes: list[Dict[str, Any]] = []
    for phase in phases:
        tasks = phase.get("tasks")
        if not isinstance(tasks, list):
            continue
        new_tasks: list[Dict[str, Any]] = []
        for task in tasks:
            if not isinstance(task, dict):
                new_tasks.append(task)
                continue
            updated, normalized = _normalize_task_packaging(task)
            new_tasks.append(normalized)
            if updated:
                changes.append(
                    {
                        "phase_id": phase.get("id") or phase.get("phase_id"),
                        "task_id": normalized.get("task_id"),
                    }
                )
        phase["tasks"] = new_tasks

    if changes:
        _append_causal_entry(
            workflow,
            {
                "timestamp": _utc_timestamp(),
                "change_type": "task_packaging_normalized",
                "source": change_source,
                "rationale": (
                    "Ensure tasks declare stable ids, prerequisites, and expected outputs."
                ),
                "evidence": {
                    "normalized_tasks": changes,
                },
                "impact_analysis": {
                    "affected_tasks": [item["task_id"] for item in changes],
                    "checks": [
                        "task_id_present",
                        "prerequisites_present",
                        "expected_outputs_present",
                    ],
                },
                "alternatives_considered": [
                    "Allow implicit task contracts without normalization",
                ],
            },
        )


def _collect_tasks(workflow: Dict[str, Any]) -> dict[str, Dict[str, Any]]:
    tasks_by_id: dict[str, Dict[str, Any]] = {}
    for phase in workflow.get("phases", []) or []:
        tasks = phase.get("tasks")
        if not isinstance(tasks, list):
            continue
        for task in tasks:
            if not isinstance(task, dict):
                continue
            task_id = task.get("task_id") or task.get("id")
            if task_id:
                tasks_by_id[str(task_id)] = task
    return tasks_by_id


def _collect_task_outputs(workflow: Dict[str, Any]) -> set[str]:
    outputs: set[str] = set()
    for phase in workflow.get("phases", []) or []:
        tasks = phase.get("tasks")
        if not isinstance(tasks, list):
            continue
        for task in tasks:
            if not isinstance(task, dict):
                continue
            for output in task.get("expected_outputs", []) or []:
                outputs.add(str(output))
            for output in task.get("outputs", []) or []:
                outputs.add(str(output))
    return outputs


def _apply_inheritance_checks(
    workflow: Dict[str, Any],
    *,
    change_source: str,
) -> None:
    inheritance = workflow.get("inheritance")
    if not isinstance(inheritance, dict) or not inheritance:
        return

    host_domain = inheritance.get("host_domain")
    donor_domains = inheritance.get("donor_domains") or []
    if not host_domain or not isinstance(donor_domains, list) or not donor_domains:
        raise ValueError("Inheritance requires host_domain and donor_domains.")

    conflict_rules = inheritance.get("conflict_rules") or {}
    precedence = conflict_rules.get("precedence") or []
    strategy = conflict_rules.get("strategy")
    if not precedence or host_domain not in precedence or not strategy:
        raise ValueError("Inheritance conflict_rules must define precedence and strategy.")

    glossary = inheritance.get("glossary") or {}
    if glossary:
        term_map: dict[str, dict[str, str]] = {}
        for domain, terms in glossary.items():
            if not isinstance(terms, dict):
                continue
            for term, definition in terms.items():
                term_map.setdefault(str(term), {})[str(domain)] = str(definition)

        collisions: dict[str, dict[str, str]] = {}
        for term, definitions in term_map.items():
            unique_defs = set(definitions.values())
            if len(definitions) > 1 and len(unique_defs) > 1:
                collisions[term] = definitions

        if collisions:
            resolutions = inheritance.get("term_resolution") or {}
            unresolved = {
                term: defs
                for term, defs in collisions.items()
                if term not in resolutions
            }
            if unresolved:
                raise ValueError(
                    f"Unresolved term collisions in inheritance glossary: {sorted(unresolved)}"
                )

    imports = inheritance.get("imports") or []
    tasks_by_id = _collect_tasks(workflow)
    outputs = _collect_task_outputs(workflow)
    prerequisite_overrides = set(
        inheritance.get("prerequisite_overrides") or []
    )

    provenance_updates: list[dict[str, str]] = []
    missing_prereqs: dict[str, list[str]] = {}

    for item in imports:
        if not isinstance(item, dict):
            continue
        domain = item.get("domain")
        version = item.get("version")
        if not domain or not version:
            raise ValueError("Inheritance imports require domain and version.")
        for task_id in item.get("task_ids", []) or []:
            task = tasks_by_id.get(str(task_id))
            if task is None:
                raise ValueError(f"Imported task {task_id} not found in workflow.")
            origin = task.get("origin") or {}
            if origin.get("domain") != domain or origin.get("version") != version:
                task["origin"] = {
                    "domain": domain,
                    "version": version,
                    "source_task_id": str(task_id),
                }
                provenance_updates.append(
                    {"task_id": str(task_id), "domain": str(domain)}
                )

            prereqs = task.get("prerequisites") or []
            missing = [
                str(req)
                for req in prereqs
                if str(req) not in outputs and str(req) not in prerequisite_overrides
            ]
            if missing:
                missing_prereqs[str(task_id)] = missing

    if missing_prereqs:
        raise ValueError(
            f"Imported tasks missing prerequisites: {sorted(missing_prereqs)}"
        )

    if provenance_updates:
        _append_causal_entry(
            workflow,
            {
                "timestamp": _utc_timestamp(),
                "change_type": "inheritance_provenance_applied",
                "source": change_source,
                "rationale": "Ensure imported tasks carry origin domain/version.",
                "evidence": {
                    "provenance_updates": provenance_updates,
                },
                "impact_analysis": {
                    "affected_tasks": [item["task_id"] for item in provenance_updates],
                    "checks": [
                        "origin_metadata_present",
                        "inheritance_imports_validated",
                    ],
                },
                "alternatives_considered": [
                    "Allow imports without explicit provenance metadata",
                ],
            },
        )


def _apply_meta_metrics(
    workflow: Dict[str, Any],
    *,
    quality_report: Dict[str, Any],
) -> None:
    workflow_id = workflow.get("workflow_id", "unnamed_workflow")
    baseline_scores = None
    baseline_overall = None
    baseline_status = "missing"

    baseline = MemoryStore().load_latest(str(workflow_id))
    if baseline:
        baseline_meta = baseline.get("evaluation", {}).get("meta_metrics", {})
        baseline_scores = baseline_meta.get("scores")
        baseline_overall = baseline_meta.get("overall_score")
        if baseline_scores is None:
            baseline_scores = baseline.get("evaluation", {}).get("quality", {}).get("metrics")
            baseline_overall = baseline.get("evaluation", {}).get("quality", {}).get("overall_score")
        if baseline_scores is not None:
            baseline_status = "loaded"

    scores = quality_report.get("metrics", {})
    overall = quality_report.get("overall_score", 0.0)
    deltas = {}
    if baseline_scores:
        for key, value in scores.items():
            base_value = baseline_scores.get(key)
            if base_value is not None:
                deltas[key] = value - base_value

    if baseline_overall is None and baseline_scores:
        baseline_overall = sum(baseline_scores.values()) / max(len(baseline_scores), 1)

    thresholds = {
        "promotion_threshold": 0.02,
        "regression_guard": -0.05,
        "guard_metrics": [
            "clarity",
            "coherence",
            "completeness",
            "intent_alignment",
            "usability",
        ],
    }

    overall_delta = None
    if baseline_overall is not None:
        overall_delta = overall - baseline_overall

    guard_metrics = thresholds["guard_metrics"]
    regression_guard = thresholds["regression_guard"]
    regression_guard_passed = True
    if deltas:
        regression_guard_passed = all(
            deltas.get(metric, 0.0) >= regression_guard for metric in guard_metrics
        )

    promotion_threshold = thresholds["promotion_threshold"]
    promotion_eligible = False
    if overall_delta is not None:
        promotion_eligible = overall_delta >= promotion_threshold and regression_guard_passed

    meta_metrics = {
        "timestamp": _utc_timestamp(),
        "scores": scores,
        "overall_score": overall,
        "baseline": {
            "status": baseline_status,
            "overall_score": baseline_overall,
            "scores": baseline_scores,
        },
        "deltas": {
            "overall_score": overall_delta,
            "metrics": deltas,
        },
        "thresholds": thresholds,
        "decision": {
            "promotion_eligible": promotion_eligible,
            "regression_guard_passed": regression_guard_passed,
        },
        "evidence_notes": [
            "Core metrics computed on the current workflow snapshot.",
            "Baseline compared against latest stored workflow version.",
        ],
    }

    workflow.setdefault("evaluation", {})["meta_metrics"] = meta_metrics


def _apply_dependency_tracking(
    workflow: Dict[str, Any],
    *,
    change_source: str,
) -> None:
    modules = workflow.get("modules", []) or []
    module_ids = {
        str(module.get("module_id"))
        for module in modules
        if module.get("module_id")
    }
    before_snapshot = _snapshot_dependencies(modules)
    missing_dependencies = {
        module_id: sorted([dep for dep in deps if dep not in module_ids])
        for module_id, deps in before_snapshot.items()
        if any(dep not in module_ids for dep in deps)
    }

    dg = DependencyGraph(modules)
    dg.autocorrect_missing_dependencies()

    cycle_detected = dg.detect_cycle()
    cycle_corrected = False
    if cycle_detected:
        logger.warning("Dependency cycle detected; attempting autocorrect.")
        cycle_corrected = dg.attempt_autocorrect_cycle()
        if not cycle_corrected and workflow.get("evaluation") is not None:
            workflow["evaluation"].setdefault("notes", []).append(
                "Unresolved dependency cycle detected; manual review required.",
            )

    after_snapshot = _snapshot_dependencies(modules)
    dependency_graph = _build_dependency_graph(modules)
    dependency_index = _build_dependency_index(modules)
    workflow["dependency_graph"] = dependency_graph
    workflow["dependency_index"] = dependency_index

    changes = {
        module_id: {
            "before": before_snapshot.get(module_id, []),
            "after": after_snapshot.get(module_id, []),
        }
        for module_id in sorted(set(before_snapshot) | set(after_snapshot))
        if before_snapshot.get(module_id, []) != after_snapshot.get(module_id, [])
    }

    if missing_dependencies or changes or cycle_detected:
        affected_modules = sorted(changes.keys())
        impacted_modules = sorted(
            {
                *affected_modules,
                *[
                    dep
                    for module_id in affected_modules
                    for dep in dependency_index.get("downstream", {}).get(module_id, [])
                ],
            }
        )
        _append_causal_entry(
            workflow,
            {
                "timestamp": _utc_timestamp(),
                "change_type": "dependency_autocorrect",
                "source": change_source,
                "rationale": (
                    "Normalize dependency references and resolve cycles to keep "
                    "execution ordering deterministic."
                ),
                "evidence": {
                    "missing_dependencies": missing_dependencies,
                    "cycle_detected": cycle_detected,
                    "cycle_corrected": cycle_corrected,
                    "changes": changes,
                },
                "impact_analysis": {
                    "affected_modules": affected_modules,
                    "downstream_impacts": impacted_modules,
                    "checks": [
                        "missing_dependency_scan",
                        "dependency_cycle_check",
                    ],
                },
                "alternatives_considered": [
                    "Manual dependency remediation without autocorrect",
                ],
            },
        )


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

    checkpoint_manager = EvaluationCheckpointer()

    orchestrator = Orchestrator()
    workflow_obj = Workflow(workflow)
    orchestrator.telemetry.record("loaded_via_orchestrator", {"workflow_id": workflow_obj.id})

    # 1. Normalize task packaging for modular reuse
    _apply_task_packaging(workflow, change_source="initial_pass")

    # 2. Validate inheritance requirements for multi-domain workflows
    _apply_inheritance_checks(workflow, change_source="initial_pass")

    # 3. Schema validation
    # 1. Schema validation
    ok, errors = validate_workflow(workflow)
    if not ok and errors:
        logger.warning("Initial schema validation reported issues: %s", errors)
        workflow.setdefault("evaluation", {}).setdefault(
            "notes",
            [],
        ).append("Schema validation reported issues; see logs for details.")

    # 4. Build dependency graph and autocorrect structural issues
    _apply_dependency_tracking(workflow, change_source="initial_pass")

    # 5. Generate mermaid representation (for logging/debugging)
    mermaid = mermaid_from_workflow(workflow)
    logger.info("Mermaid graph for workflow %s:\n%s", workflow_id, mermaid)

    # 6. Evaluation + semantic scoring
    base_quality = evaluate_workflow_quality(workflow)
    workflow.setdefault("evaluation", {})["quality"] = base_quality
    base_checkpoint = checkpoint_manager.record(
        "baseline_quality",
        {
            "overall_score": base_quality.get("overall_score", 0.0),
            **(base_quality.get("metrics") or {}),
        },
        notes=["Initial evaluation before refinement."],
    )
    workflow.setdefault("evaluation", {}).setdefault("checkpoints", []).append(
        base_checkpoint.to_dict()
    )
    _apply_meta_metrics(workflow, quality_report=base_quality)

    # 7. Recursive refinement (single iteration) if enabled
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
        after_quality = outcome.after_report.get("quality", {}) or {}
        refined_checkpoint = checkpoint_manager.record(
            "post_refinement",
            {
                "overall_score": after_quality.get("overall_score", 0.0),
                **(after_quality.get("metrics") or {}),
            },
            notes=[
                "Post-refinement evaluation checkpoint",
                f"Semantic delta: {outcome.semantic_delta:.3f}",
            ],
        )
        refined_eval = refined.setdefault("evaluation", {})
        refined_eval.setdefault("checkpoints", []).append(refined_checkpoint.to_dict())
        refined_eval["checkpoint_summary"] = checkpoint_manager.summarize()
        refined_quality = outcome.after_report.get("quality")
        if isinstance(refined_quality, dict):
            refined.setdefault("evaluation", {})["quality"] = refined_quality
            _apply_meta_metrics(refined, quality_report=refined_quality)
        diff_summary = compute_diff_summary(workflow, refined)
        _append_causal_entry(
            refined,
            {
                "timestamp": _utc_timestamp(),
                "change_type": "workflow_refinement",
                "source": "recursive_refinement",
                "rationale": refined.get("recursion_metadata", {}).get(
                    "llm_reasoning", "Refinement requested by recursion policy."
                ),
                "evidence": {
                    "score_delta": outcome.score_delta,
                    "semantic_delta": outcome.semantic_delta,
                    "decision": refined.get("recursion_metadata", {}).get("llm_decision"),
                    "diff_summary": diff_summary,
                },
                "impact_analysis": {
                    "changed_fields": diff_summary.get("changed_fields", []),
                    "checks": ["evaluation_delta", "semantic_delta"],
                },
                "alternatives_considered": [
                    "Retain baseline workflow without refinement",
                ],
            },
        )
        log_event(
            "mvm.process.refined",
            {
                "workflow_id": refined.get("workflow_id", workflow_id),
                "score_delta": outcome.score_delta,
                "semantic_delta": outcome.semantic_delta,
            },
        )
        _apply_task_packaging(refined, change_source="refinement_pass")
        _apply_inheritance_checks(refined, change_source="refinement_pass")
        _apply_dependency_tracking(refined, change_source="refinement_pass")

    if not enable_refinement:
        workflow.setdefault("evaluation", {})[
            "checkpoint_summary"
        ] = checkpoint_manager.summarize()

    # 6. Export updated visualization assets
    # 8. Export updated visualization assets
    export_graphviz(refined, str(out_dir))
    viz_export_json(refined, str(out_dir))
    viz_export_markdown(refined, str(out_dir))

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
        orchestrator = Orchestrator()
        context = RunContext(
            workflow_source=workflow_source,
            runner=run_mvm,
            runner_kwargs={
                "out_dir": out_dir,
                "enable_refinement": not args.no_refine,
                "enable_history": not args.no_history,
                "preview": args.preview,
            },
        )
        result = orchestrator.run_mvm(context)
        refined = result.workflow_data or result.workflow.to_dict()
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
