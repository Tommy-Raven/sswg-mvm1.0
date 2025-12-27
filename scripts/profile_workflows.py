#!/usr/bin/env python3
"""
Collect per-phase timing + memory profiling snapshots for mvm workflows.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
import tracemalloc
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ai_evaluation.evaluation_engine import evaluate_workflow_quality
from ai_monitoring.structured_logger import log_event
from ai_validation.schema_validator import validate_workflow
from ai_visualization.mermaid_generator import mermaid_from_workflow
from generator import main as mvm_main


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _measure_phase(
    label: str,
    func: Callable[[], Any],
) -> Tuple[Any, Dict[str, Any]]:
    tracemalloc.start()
    start = time.perf_counter()
    result = func()
    duration = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    snapshot = {
        "duration_sec": duration,
        "memory_current_kib": current / 1024.0,
        "memory_peak_kib": peak / 1024.0,
    }
    return result, snapshot


def _summarize_total(phases: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
    total_duration = sum(phase["duration_sec"] for phase in phases.values())
    peak_memory = max(
        (phase["memory_peak_kib"] for phase in phases.values()),
        default=0.0,
    )
    return {
        "duration_sec": total_duration,
        "peak_memory_kib": peak_memory,
    }


def _safe_validate_workflow(workflow: Dict[str, Any]) -> Tuple[bool, list[str], str | None]:
    try:
        ok, errors = validate_workflow(workflow)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        return False, [], str(exc)
    return bool(ok), [str(error) for error in (errors or [])], None


def _write_anchor(artifact_path: Path) -> Path:
    anchor_path = Path(f"{artifact_path}.anchor.json")
    anchor = {
        "anchor_id": "profiling_artifact",
        "anchor_version": "1.0",
        "scope": "profiling",
        "owner": "scripts.profile_workflows",
        "status": "draft",
        "artifact_path": str(artifact_path),
    }
    anchor_path.write_text(json.dumps(anchor, indent=2), encoding="utf-8")
    return anchor_path


def profile_workflow(workflow_path: Path, *, out_dir: Path) -> Dict[str, Any]:
    phases: Dict[str, Dict[str, Any]] = {}

    workflow, phases["load_workflow"] = _measure_phase(
        "load_workflow", lambda: mvm_main.load_workflow(workflow_path)
    )
    workflow = deepcopy(workflow)

    _, phases["normalize_task_packaging"] = _measure_phase(
        "normalize_task_packaging",
        lambda: mvm_main._apply_task_packaging(
            workflow, change_source="profiling_run"
        ),
    )

    _, phases["inheritance_checks"] = _measure_phase(
        "inheritance_checks",
        lambda: mvm_main._apply_inheritance_checks(
            workflow, change_source="profiling_run"
        ),
    )

    (schema_ok, schema_errors, schema_exception), phases["schema_validation"] = _measure_phase(
        "schema_validation",
        lambda: _safe_validate_workflow(workflow),
    )
    phases["schema_validation"]["details"] = {
        "ok": bool(schema_ok),
        "error_count": len(schema_errors or []),
        "exception": schema_exception,
    }

    _, phases["dependency_graph"] = _measure_phase(
        "dependency_graph",
        lambda: mvm_main._apply_dependency_tracking(
            workflow, change_source="profiling_run"
        ),
    )

    mermaid, phases["mermaid_render"] = _measure_phase(
        "mermaid_render",
        lambda: mermaid_from_workflow(workflow),
    )
    phases["mermaid_render"]["details"] = {
        "mermaid_length": len(mermaid or ""),
    }

    quality, phases["evaluation_scoring"] = _measure_phase(
        "evaluation_scoring",
        lambda: evaluate_workflow_quality(workflow),
    )
    phases["evaluation_scoring"]["details"] = {
        "overall_score": quality.get("overall_score", 0.0),
    }

    workflow.setdefault("evaluation", {})["quality"] = quality
    _, phases["meta_metrics"] = _measure_phase(
        "meta_metrics",
        lambda: mvm_main._apply_meta_metrics(workflow, quality_report=quality),
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts, phases["export_artifacts"] = _measure_phase(
        "export_artifacts",
        lambda: mvm_main.export_artifacts(workflow, out_dir),
    )
    anchor_paths = []
    for artifact_path in (artifacts or {}).values():
        anchor_paths.append(_write_anchor(Path(artifact_path)))
    phases["export_artifacts"]["details"] = {
        "artifacts": artifacts or {},
        "anchors": [str(path) for path in anchor_paths],
    }

    return {
        "workflow_path": str(workflow_path),
        "workflow_id": workflow.get("workflow_id"),
        "phases": phases,
        "totals": _summarize_total(phases),
    }


def build_snapshot(workflows: list[Path], *, out_dir: Path) -> Dict[str, Any]:
    snapshot = {
        "anchor": {
            "anchor_id": "performance_profiling_snapshot",
            "anchor_version": "1.0",
            "scope": "profiling",
            "owner": "scripts.profile_workflows",
            "status": "draft",
        },
        "timestamp_utc": _timestamp(),
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        },
        "workloads": [],
    }

    for workflow_path in workflows:
        workload_name = workflow_path.stem
        workload_out_dir = out_dir / workload_name
        workload_snapshot = profile_workflow(workflow_path, out_dir=workload_out_dir)
        workload_snapshot["name"] = workload_name
        snapshot["workloads"].append(workload_snapshot)

    return snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Profile mvm workflow phases for timing + memory snapshots.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/profiling"),
        help="Directory to store profiling snapshots.",
    )
    parser.add_argument(
        "--templates",
        nargs="+",
        default=[
            "data/templates/campfire_workflow.json",
            "data/templates/technical_procedure_template.json",
        ],
        help="Workflow template JSON paths to profile.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workflows = [Path(path) for path in args.templates]
    snapshot = build_snapshot(workflows, out_dir=args.output_dir)

    date_slug = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_path = args.output_dir / f"workflow_profiling_{date_slug}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    log_event(
        "profiling.snapshot_written",
        {"path": str(output_path), "workloads": len(snapshot["workloads"])},
    )
    print(f"Wrote profiling snapshot to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
