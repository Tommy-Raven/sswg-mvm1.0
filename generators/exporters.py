import json
from utils import log

def export_markdown(workflow):
    log(f"Exporting workflow {workflow.workflow_id} to Markdown")
    md_content = f"# Workflow {workflow.workflow_id}\n\nObjective: {workflow.objective}\n\n"
    md_content += "## Stages\n"
    for stage, steps in workflow.structured_instruction.items():
        md_content += f"### {stage}\n"
        for step in steps:
            md_content += f"- {step}\n"
    md_content += "\n## Modules\n"
    md_content += f"{str(workflow.modular_workflow['modules'])}\n"
    md_content += "\n## Dependencies\n"
    for dep in workflow.modular_workflow['dependencies']:
        md_content += f"- {dep}\n"
    md_content += "\n## Evaluation Report\n"
    for k, v in workflow.evaluation_report.items():
        md_content += f"- {k.capitalize()}: {v}\n"
    filename = f"templates/{workflow.workflow_id}.md"
    with open(filename, "w") as f:
        f.write(md_content)
    log(f"Markdown saved as {filename}")

def export_json(workflow):
    log(f"Exporting workflow {workflow.workflow_id} to JSON")
    data = {
        "workflow_id": workflow.workflow_id,
        "objective": workflow.objective,
        "stages": workflow.structured_instruction,
        "modules": workflow.modular_workflow,
        "evaluation_report": workflow.evaluation_report,
        "improved_workflow": workflow.improved_workflow,
    }
    filename = f"templates/{workflow.workflow_id}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    log(f"JSON saved as {filename}")