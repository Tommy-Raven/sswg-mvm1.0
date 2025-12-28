"""Tests for workflow export helper functions."""

import os

from generator.exporters import export_json, export_markdown
from tests.assertions import require


def test_export_workflow_json_and_md(tmp_path):
    wf = {
        "workflow_id": "test",
        "version": "v.09.mvm.25",
        "metadata": {"purpose": "test"},
        "phases": [],
    }

    json_out = export_json(wf, out_dir=str(tmp_path))
    md_out = export_markdown(wf, out_dir=str(tmp_path))

    require(os.path.exists(json_out), "Expected JSON export to exist")
    require(os.path.exists(md_out), "Expected Markdown export to exist")
