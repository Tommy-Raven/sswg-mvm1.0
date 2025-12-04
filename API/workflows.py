#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API.workflows — High-Level Workflow Interfaces
SSWG-MVM v.09.mvm.25

This module provides a programmatic interface for loading, validating,
refining, exporting, and inspecting SSWG workflow objects.

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
from generator.main import run_mvm, load_workflow, process_workflow

# Validation
from ai_validation.schema_validator import validate_workflow

# Refiner (MVM-lite recursion)
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
def validate(workflow: Dict[str, Any]) -> tuple[bool, str]:
    """
