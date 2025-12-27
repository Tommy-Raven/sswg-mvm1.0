"""Tests for exporter helper functions."""

from generator.exporters import export_json, export_markdown
import os

def test_json_markdown_exports(tmp_path):
    wf = {
        "workflow_id": "exp_test",
        "version": "v.09.mvm.25",
        "metadata": {"purpose": "Unit test"},
        "phases": [],
    }

    json_out = export_json(wf, tmp_path)
    md_out = export_markdown(wf, tmp_path)

    assert all(os.path.exists(p) for p in [json_out, md_out])
