#!/usr/bin/env python3
"""
generator/exporters.py — Workflow Export Utilities for SSWG MVM

Exports:
 - JSON (schema-aligned)
 - Markdown (human-readable)
 - Async combined export

Assumes a dict-based workflow structure consistent with workflow_schema.json:
{
  "workflow_id": "wf_campfire_001",
  "version": "0.0.1",
  "schema_version": "1.0.0",
  "metadata": {...},
  "phases": [...],
  "modules": [...],
  "outputs": [...],
  "evaluation": {...},
  "recursion": {...}
}
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

from ai_monitoring.structured_logger import log_event


# ─── Directory Utilities ───────────────────────────────────────────
def ensure_dir_exists(path: str | Path) -> None:
    """Ensure the directory for a given path exists."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)


# ─── JSON Export ──────────────────────────────────────────────────
def export_json(workflow: Dict[str, Any], out_dir: str = "data/outputs") -> str:
    """
    Export a workflow (dict-based) to JSON using a schema-aligned structure.

    Args:
        workflow: Workflow object as Python dict.
        out_dir: Output directory.

    Returns:
        Path to the JSON file (as string).
    """
    ensure_dir_exists(out_dir)

    workflow_id = workflow.get("workflow_id", "unnamed_workflow")
    filename = Path(out_dir) / f"{workflow_id}.json"

    log_event(
        "export.json.started",
        {"workflow_id": workflow_id, "path": str(filename)},
    )

    data: Dict[str, Any] = {
        "workflow_id": workflow_id,
        "version": workflow.get("version", "0.0.0"),
        "schema_version": workflow.get("schema_version", "1.0.0"),
        "metadata": workflow.get("metadata", {}),
        "phases": workflow.get("phases", []),
        "modules": workflow.get("modules", []),
        "outputs": workflow.get("outputs", []),
        "evaluation": workflow.get("evaluation", {}),
        "recursion": workflow.get("recursion", {}),
    }

    filename.write_text(json.dumps(data, indent=2), encoding="utf-8")

    log_event(
        "export.json.completed",
        {"workflow_id": workflow_id, "path": str(filename)},
    )
    return str(filename)


# ─── Markdown Export ──────────────────────────────────────────────
def export_markdown(workflow: Dict[str, Any], out_dir: str = "data/outputs") -> str:
    """
    Human-readable Markdown export for debugging & documentation.

    Args:
        workflow: Dict describing workflow.
        out_dir: Output directory.

    Returns:
        Path to the Markdown file (as string).
    """
    ensure_dir_exists(out_dir)

    workflow_id = workflow.get("workflow_id", "unnamed_workflow")
    filename = Path(out_dir) / f"{workflow_id}.md"

    log_event(
        "export.md.started",
        {"workflow_id": workflow_id, "path": str(filename)},
    )

    md: List[str] = []
    md.append(f"# Workflow: {workflow_id}\n")
    md.append(f"**Version:** {workflow.get('version', '0.0.0')}")
    md.append(f"**Schema Version:** {workflow.get('schema_version', '1.0.0')}\n")

    # Metadata
    meta = workflow.get("metadata", {})
    if meta:
        md.append("## Metadata")
        for k, v in meta.items():
            md.append(f"- **{k}**: {v}")
        md.append("")

    # Phases
    phases = workflow.get("phases", [])
    if phases:
        md.append("## Phases")
        for ph in phases:
            name = ph.get("name") or ph.get("phase_id") or "Unnamed phase"
            md.append(f"### {name}")
            desc = ph.get("description") or ""
            if desc:
                md.append(desc)
            md.append("")
    
    # Modules
    modules = workflow.get("modules", [])
    if modules:
        md.append("## Modules")
        for m in modules:
            name = m.get("name") or m.get("module_id") or "Unnamed module"
            md.append(f"### {name}")
            md.append(f"- **ID:** {m.get('module_id')}")
            md.append(f"- **Phase:** {m.get('phase_id')}")
            md.append(f"- **Inputs:** {m.get('inputs', [])}")
            md.append(f"- **Outputs:** {m.get('outputs', [])}")
            md.append(f"- **Dependencies:** {m.get('dependencies', [])}")
            md.append(f"- **AI Logic:** {m.get('ai_logic', '')}")
            md.append(f"- **Human Actionable:** {m.get('human_actionable', '')}")
            md.append("")

    # Evaluation
    eval_block = workflow.get("evaluation", {})
    if eval_block:
        md.append("## Evaluation Report")
        for k, v in eval_block.items():
            md.append(f"- **{k.capitalize()}**: {v}")
        md.append("")

    # Recursion metadata
    rec = workflow.get("recursion", {})
    if rec:
        md.append("## Recursion Parameters")
        for k, v in rec.items():
            md.append(f"- **{k}**: {v}")
        md.append("")

    filename.write_text("\n".join(md), encoding="utf-8")

    log_event(
        "export.md.completed",
        {"workflow_id": workflow_id, "path": str(filename)},
    )

    return str(filename)


# ─── Async Helpers ───────────────────────────────────────────────
async def run_task(
    task_func: Callable[..., Awaitable[Any]], *args, **kwargs
) -> Any:
    """
    Run an async task and catch exceptions.

    Args:
        task_func: Async function to run.

    Returns:
        The result of the async function, or None if it failed.
    """
    try:
        return await task_func(*args, **kwargs)
    except Exception as e:
        log_event(
            "export.async.error",
            {"error": str(e), "task": getattr(task_func, "__name__", repr(task_func))},
        )
        return None


async def export_workflow_async(
    workflow: Dict[str, Any], out_dir: str = "data/outputs"
) -> None:
    """
    Run both export tasks asynchronously.
    """
    await asyncio.gather(
        run_task(lambda wf, d: asyncio.to_thread(export_json, wf, d), workflow, out_dir),
        run_task(lambda wf, d: asyncio.to_thread(export_markdown, wf, d), workflow, out_dir),
    )
# ----------------------------------------------------------------------