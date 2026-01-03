---
anchor:
  anchor_id: examples_readme
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# Examples

These scripts demonstrate how to run the visualization utilities without
embedding file-writing demo blocks in library modules.

## Expected inputs/outputs

- `export_workflow_demo.py` writes Graphviz, JSON, and Markdown workflow exports
  under `./build/` with timestamped filenames.
- `import_markdown_demo.py` reads a Markdown workflow file (default
  `./build/workflow_demo.md`) and writes a JSON workflow export under
  `./data/workflows/`.
- `mermaid_demo.py` prints a Mermaid flowchart to stdout and does not write
  files.

Run them from the repository root so the default relative paths resolve.
