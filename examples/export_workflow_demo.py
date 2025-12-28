#!/usr/bin/env python3
"""
Export workflow demo.

Outputs:
- Graphviz DOT, JSON, and Markdown files under ./build/ with timestamped names.
"""

from ai_visualization.export_manager import export_workflow


def main() -> None:
    wf_demo = {
        "workflow_id": "demo_workflow",
        "version": "1.0",
        "metadata": {"purpose": "Testing export manager", "audience": "Developers"},
        "phases": [
            {
                "title": "Phase 1: Initialization",
                "tasks": ["Collect user inputs", "Load template"],
            },
            {
                "title": "Phase 2: Generation",
                "tasks": ["Assemble structure", "Export results"],
            },
        ],
        "dependency_graph": {
            "nodes": ["Init", "Generate"],
            "edges": [["Init", "Generate"]],
        },
    }

    exported = export_workflow(wf_demo, export_mode="both")
    print("Export complete:", exported)


if __name__ == "__main__":
    main()
