#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API.workflows — High-Level Workflow Interfaces
sswg-mvm v.09.mvm.25

Public API: stable

This module provides a programmatic interface for loading, validating,
refining, exporting, and inspecting sswg workflow objects.

It is a thin integration layer across:
    - generator.main
    - ai_validation (schema validator)
    - ai_graph (dependency mapper)
    - ai_visualization (Mermaid / DOT)
    - generator.exporters (JSON/Markdown)
    - generator.recursion_manager (simple refiner)

Authors:
    Tommy Raven / Thomas Byers
    Raven Recordings, LLC © 2025

Version:
    v.09.mvm.25
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

# Core pipeline
from generator.pdl_validator import (
    PDLValidationError,
    validate_pdl_file,
    validate_pdl_object,
)

# Validation
from ai_validation.schema_validator import validate_workflow

# Refiner (mvm-lite recursion)
from generator.recursion_manager import simple_refiner

# Exporters
from generator.exporters import export_json, export_markdown

# Visualization
from ai_visualization.mermaid_generator import mermaid_from_workflow


# ------------------------------------------------------------
# WORKFLOW LOADING
# ------------------------------------------------------------
def load_workflow_file(path: str | Path) -> Dict[str, Any]:
    """
    Load a workflow JSON from disk.

    Raises:
        FileNotFoundError
        JSONDecodeError
    """
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8"))


def load_template(slug: str) -> Dict[str, Any]:
    """
    Load a template workflow by slug from data/templates/.
    """
    template_path = Path("data/templates") / f"{slug}_template.json"
    return load_workflow_file(template_path)


# ------------------------------------------------------------
# VALIDATION
# ------------------------------------------------------------
def validate(
    workflow: Dict[str, Any],
    *,
    pdl: Dict[str, Any] | str | Path | None = None,
) -> tuple[bool, str]:
    """
    Public API: stable

    Validate a workflow dictionary against the workflow schema and
    optionally validate a PDL document when supplied.

    Returns:
        (ok, message)
        ok: bool — True if validation passed
        message: details or "ok"
    """
    ok, errors = validate_workflow(workflow)
    if not ok:
        return False, _format_schema_errors(errors)

    if pdl is None:
        return True, "ok"

    try:
        if isinstance(pdl, (str, Path)):
            validate_pdl_file(Path(pdl))
        else:
            validate_pdl_object(pdl)
    except PDLValidationError as exc:
        return False, json.dumps(exc.label.as_dict(), indent=2)

    return True, "ok"


def _format_schema_errors(errors: Optional[Any]) -> str:
    if not errors:
        return "Schema validation failed."
    if isinstance(errors, str):
        return errors
    return "; ".join(
        f"{error.message} at {list(error.path)}" for error in errors
    )


def refine(
    workflow: Dict[str, Any],
    *,
    depth: int = 1,
    out_dir: str | Path = "data/outputs",
) -> Dict[str, Any]:
    """
    Public API: stable

    Perform recursive refinement passes using the mvm refiner.
    """
    refined = workflow
    for _ in range(max(depth, 0)):
        refined = simple_refiner(refined, output_dir=Path(out_dir))
    return refined


def export(
    workflow: Dict[str, Any],
    *,
    out_dir: str | Path = "data/outputs",
) -> Dict[str, str]:
    """
    Public API: stable

    Export workflow artifacts to JSON and Markdown.
    """
    out_dir_str = str(out_dir)
    return {
        "json": export_json(workflow, out_dir_str),
        "markdown": export_markdown(workflow, out_dir_str),
    }


def generate_mermaid(workflow: Dict[str, Any]) -> str:
    """
    Public API: stable

    Generate a Mermaid diagram representation of a workflow.
    """
    return mermaid_from_workflow(workflow)


def get_metadata(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Public API: stable

    Return the metadata section of the workflow.
    """
    return dict(workflow.get("metadata", {}) or {})


def get_phases(workflow: Dict[str, Any]) -> list[Dict[str, Any]]:
    """
    Public API: stable

    Return the workflow phases list.
    """
    phases = workflow.get("phases", []) or []
    return list(phases)


def get_dependency_graph(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Public API: stable

    Return the dependency graph if present, otherwise build a simple graph
    from module dependencies.
    """
    dependency_graph = workflow.get("dependency_graph")
    if isinstance(dependency_graph, dict):
        return dict(dependency_graph)
    modules = workflow.get("modules", []) or []
    return _build_dependency_graph(modules)


def _build_dependency_graph(modules: list[Dict[str, Any]]) -> Dict[str, Any]:
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
