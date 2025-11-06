import os
import json
from utils import log

def ensure_dir_exists(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def export_markdown(workflow, out_dir="templates"):
    """Export workflow to Markdown format."""
    ensure_dir_exists(out_dir)
    filename = os.path.join(out_dir, f"{workflow.workflow_id}.md")

    log(f"Exporting workflow {workflow.workflow_id} → Markdown")
    md_content = f"# Workflow {workflow.workflow_id}\n\n"
    md_content += f"**Objective:** {workflow.objective}\n\n## Stages\n"

    for stage, steps in workflow.structured_instruction.items():
        md_content += f"### {stage}\n"
        for step in steps:
            md_content += f"- {step}\n"

    md_content += "\n## Modules\n"
    md_content += json.dumps(workflow.modular_workflow.get("modules", {}), indent=2)
    md_content += "\n\n## Dependencies\n"
    for dep in workflow.modular_workflow.get("dependencies", []):
        md_content += f"- {dep}\n"

    md_content += "\n\n## Evaluation Report\n"
    for k, v in (workflow.evaluation_report or {}).items():
        md_content += f"- {k.capitalize()}: {v}\n"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(md_content)

    log(f"Markdown saved at {filename}")
    return filename


def export_json(workflow, out_dir="templates"):
    """Export workflow to JSON format."""
    ensure_dir_exists(out_dir)
    filename = os.path.join(out_dir, f"{workflow.workflow_id}.json")

    log(f"Exporting workflow {workflow.workflow_id} → JSON")
    data = {
        "workflow_id": workflow.workflow_id,
        "objective": workflow.objective,
        "stages": workflow.structured_instruction,
        "modules": workflow.modular_workflow,
        "evaluation_report": workflow.evaluation_report,
        "improved_workflow": workflow.improved_workflow,
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    log(f"JSON saved at {filename}")
    return filename
