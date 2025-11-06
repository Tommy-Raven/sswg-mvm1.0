"""
Tests individual exporters (Markdown, Graphviz, JSON).
"""

from ai_visualization.export_manager import export_json, export_markdown, export_graphviz
import os


def test_json_markdown_and_dot_exports(tmp_path):
    wf = {
        "workflow_id": "exp_test",
        "version": "1.0",
        "metadata": {"purpose": "Unit test"},
        "phases": [{"title": "Phase", "tasks": ["Step 1", "Step 2"]}],
        "dependency_graph": {"nodes": ["Step 1", "Step 2"], "edges": [["Step 1", "Step 2"]]},
    }

    json_out = export_json(wf, out_dir=tmp_path)
    md_out = export_markdown(wf, out_dir=tmp_path)
    dot_out = export_graphviz(wf, out_dir=tmp_path)

    assert all(os.path.exists(f) for f in [json_out, md_out, dot_out])

