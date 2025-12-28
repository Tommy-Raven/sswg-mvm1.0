#!/usr/bin/env python3
"""
Markdown import demo.

Inputs:
- Markdown workflow file at ./build/workflow_demo.md (update as needed).

Outputs:
- JSON workflow export under ./data/workflows/ with a timestamped filename.
"""

import os

from ai_visualization.markdown_importer import import_markdown


def main() -> None:
    demo_md = "./build/workflow_demo.md"
    if os.path.exists(demo_md):
        import_markdown(demo_md)
    else:
        print(
            f"No demo Markdown file found at {demo_md}. Run export_workflow_demo first."
        )


if __name__ == "__main__":
    main()
