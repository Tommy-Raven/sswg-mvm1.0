#!/usr/bin/env python3
"""
ai_visualization/mermaid_generator.py — Mermaid diagram generator for SSWG MVM.

Converts a schema-aligned workflow dict into a Mermaid flowchart.

Expected workflow shape (minimal):
{
  "workflow_id": "wf_campfire_001",
  "modules": [
    {
      "module_id": "m01_location_check",
      "name": "Location & Permits",
      "dependencies": []
    },
    {
      "module_id": "m02_materials_gather",
      "name": "Gather materials",
      "dependencies": ["m01_location_check"]
    },
    ...
  ]
}

Output example (flowchart TD):
flowchart TD
  m01_location_check["Location & Permits"]
  m02_materials_gather["Gather materials"]
  m01_location_check --> m02_materials_gather
"""

from __future__ import annotations
from typing import Any, Dict, List


def mermaid_from_workflow(workflow: Dict[str, Any]) -> str:
    """
    Build a Mermaid flowchart from a workflow dict.

    Nodes:
      - One node per module (label = name or module_id)
    Edges:
      - For each dependency d in module.dependencies → "d --> module_id"

    Args:
        workflow: Dict representing the workflow.

    Returns:
        Mermaid flowchart string (flowchart TD).
    """
    modules: List[Dict[str, Any]] = workflow.get("modules", []) or []
    lines: List[str] = ["flowchart TD"]

    # Define nodes
    for m in modules:
        mid = m.get("module_id")
        if not mid:
            # skip malformed entries
            continue
        label = m.get("name") or mid
        # Escape quotes in label for Mermaid safety
        safe_label = str(label).replace('"', '\\"')
        lines.append(f'  {mid}["{safe_label}"]')

    # Define edges
    for m in modules:
        mid = m.get("module_id")
        if not mid:
            continue
        deps = m.get("dependencies", []) or []
        for d in deps:
            # Only draw edge if dependency has a node
            lines.append(f"  {d} --> {mid}")

    return "\n".join(lines)


# End of ai_visualization/mermaid_generator.py
