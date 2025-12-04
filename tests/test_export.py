from generator.exporters import export_json, export_markdown
import os


def test_export_workflow_json_and_md(tmp_path):
    wf = {
        "workflow_id": "test",
        "version": "v.09.mvm.25",
        "metadata": {"purpose": "test"},
        "phases": [],
    }

    json_out = export_json(wf, out_dir=str(tmp_path))
    md_out = export_markdown(wf, out_dir=str(tmp_path))

    assert os.path.exists(json_out)
    assert os.path.exists(md_out)
