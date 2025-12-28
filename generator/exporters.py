#!/usr/bin/env python3
"""
generator/exporters.py — Workflow export helpers (MVM-aware).

Supports both:
- Legacy Workflow objects (with attributes like .workflow_id, .objective, etc.)
- Plain dict-based workflows (as used by generator.main MVM entrypoint).

Exports:
- JSON: full workflow structure
- Markdown: human-readable summary
"""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Mapping as MappingABC
from dataclasses import dataclass
from typing import Any, Dict, Mapping

from generator.utils import log


def _ensure_dir(path: str) -> None:
    """Ensure the output directory exists."""
    os.makedirs(path, exist_ok=True)


def _is_mapping(obj: Any) -> bool:
    """Return True when the provided object is mapping-like."""
    return isinstance(obj, MappingABC)


@dataclass(frozen=True)
class WorkflowSections:
    """Normalized workflow sections for markdown export."""

    title: str
    objective: str | None
    phases: Any
    modules: Any
    evaluation: Any


def _extract_sections(workflow: Any, wf_id: str) -> WorkflowSections:
    """Normalize workflow fields for markdown rendering."""
    if _is_mapping(workflow):
        data = workflow
        title = data.get("title") or f"Workflow {wf_id}"
        objective = data.get("objective") or data.get("description")
        phases = data.get("phases", [])
        modules = data.get("modules", [])
        evaluation = data.get("evaluation", {})
    else:
        title = getattr(workflow, "title", f"Workflow {wf_id}")
        objective = getattr(workflow, "objective", None)
        phases = getattr(workflow, "structured_instruction", {})
        modules = getattr(workflow, "modular_workflow", {})
        evaluation = getattr(workflow, "evaluation_report", {})
    return WorkflowSections(
        title=title,
        objective=objective,
        phases=phases,
        modules=modules,
        evaluation=evaluation,
    )


def _get_workflow_id(workflow: Any) -> str:
    """Best-effort workflow ID extraction."""
    if _is_mapping(workflow):
        return str(
            workflow.get("workflow_id") or workflow.get("id") or "unnamed_workflow"
        )
    return str(getattr(workflow, "workflow_id", "unnamed_workflow"))


def export_json(workflow: Any, out_dir: str = "templates") -> str:
    """
    Export a workflow to JSON.

    - If `workflow` is a dict, it is written as-is (shallow-copied).
    - If `workflow` is an object, we project the legacy fields used in tests.
    """
    _ensure_dir(out_dir)
    wf_id = _get_workflow_id(workflow)
    filename = os.path.join(out_dir, f"{wf_id}.json")

    if _is_mapping(workflow):
        data: Dict[str, Any] = dict(workflow)  # shallow copy for safety
    else:
        # Backwards-compatible projection for legacy Workflow objects
        data = {
            "workflow_id": getattr(workflow, "workflow_id", wf_id),
            "objective": getattr(workflow, "objective", None),
            "stages": getattr(workflow, "structured_instruction", {}),
            "modules": getattr(workflow, "modular_workflow", {}),
            "evaluation_report": getattr(workflow, "evaluation_report", None),
            "improved_workflow": getattr(workflow, "improved_workflow", None),
        }

    with open(filename, "w", encoding="utf-8") as file_handle:
        json.dump(data, file_handle, indent=2)

    log(f"Exported workflow {wf_id} → JSON at {filename}")
    return filename


def export_markdown(workflow: Any, out_dir: str = "templates") -> str:
    """
    Export a workflow to a lightweight Markdown summary.

    Tries to render something sensible for both dict-based and object-based
    workflows. It is intentionally lossy and human-facing.
    """
    # pylint: disable=too-many-branches,too-many-statements,too-many-locals
    _ensure_dir(out_dir)
    wf_id = _get_workflow_id(workflow)
    filename = os.path.join(out_dir, f"{wf_id}.md")

    sections = _extract_sections(workflow, wf_id)

    md_lines: list[str] = []
    md_lines.append(f"# {sections.title}")
    md_lines.append("")
    md_lines.append(f"**Workflow ID:** `{wf_id}`")

    if sections.objective:
        md_lines.append("")
        md_lines.append(f"**Objective:** {sections.objective}")

    # ── Phases ─────────────────────────────────────────────
    md_lines.append("")
    md_lines.append("## Phases")

    # Legacy style: dict of {phase_name: [steps]}
    if isinstance(sections.phases, MappingABC):
        for name, steps in sections.phases.items():
            md_lines.append(f"### {name}")
            for step in steps or []:
                md_lines.append(f"- {step}")
    else:
        # Template style: list of phase dicts
        for idx, phase in enumerate(sections.phases):
            if isinstance(phase, MappingABC):
                pname = phase.get("name") or phase.get("id") or f"Phase {idx + 1}"
                md_lines.append(f"### {pname}")
                tasks = phase.get("tasks", [])
                for task in tasks:
                    if isinstance(task, MappingABC):
                        desc = task.get("description") or str(task)
                    else:
                        desc = str(task)
                    md_lines.append(f"- {desc}")
            else:
                md_lines.append(f"- {phase}")

    # ── Modules ────────────────────────────────────────────
    if sections.modules:
        md_lines.append("")
        md_lines.append("## Modules")
        if isinstance(sections.modules, MappingABC):
            for name, mod in sections.modules.items():
                md_lines.append(f"- **{name}**: {mod}")
        else:
            for mod in sections.modules:
                md_lines.append(f"- {mod}")

    # ── Evaluation ────────────────────────────────────────
    if sections.evaluation:
        md_lines.append("")
        md_lines.append("## Evaluation")
        if isinstance(sections.evaluation, MappingABC):
            for key, val in sections.evaluation.items():
                md_lines.append(f"- **{key}**: {val}")
        else:
            md_lines.append(f"- {sections.evaluation}")

    md_content = "\n".join(md_lines)

    with open(filename, "w", encoding="utf-8") as file_handle:
        file_handle.write(md_content)

    log(f"Exported workflow {wf_id} → Markdown at {filename}")
    return filename


async def export_workflow_async(
    workflow: Any, out_dir: str = "templates"
) -> Dict[str, str]:
    """
    Async convenience wrapper that runs the sync exporters in a thread pool.

    Returns:
        dict with keys 'json' and 'markdown'.
    """
    loop = asyncio.get_running_loop()
    out_dir_str = str(out_dir)

    json_path = await loop.run_in_executor(None, export_json, workflow, out_dir_str)
    md_path = await loop.run_in_executor(None, export_markdown, workflow, out_dir_str)
    return {"json": json_path, "markdown": md_path}
