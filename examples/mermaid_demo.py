#!/usr/bin/env python3
"""
Mermaid generator demo.

Outputs:
- Mermaid flowchart printed to stdout.
"""

from ai_visualization.mermaid_generator import mermaid_from_workflow


def main() -> None:
    example = {
        "workflow_id": "wf_example",
        "modules": [
            {"module_id": "m1", "name": "Start", "dependencies": []},
            {"module_id": "m2", "name": "Next step", "dependencies": ["m1"]},
        ],
    }
    print(mermaid_from_workflow(example))


if __name__ == "__main__":
    main()
