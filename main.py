import argparse
from workflow import Workflow
from exporters import export_markdown, export_json
from utils import generate_workflow_id, log
from recursive_expansion import recursive_expand

def parse_user_input():
    parser = argparse.ArgumentParser(description="AI Instructional Workflow Generator")
    parser.add_argument('--purpose', type=str, help="Purpose of the workflow")
    parser.add_argument('--audience', type=str, help="Target audience (e.g., beginner, expert)")
    parser.add_argument('--delivery_mode', type=str, help="Delivery modes (comma-separated, e.g., text,code)")
    parser.add_argument('--expansion_mode', type=str, help="Expansion modes (comma-separated, e.g., recursive,modular)")
    parser.add_argument('--evaluation_method', type=str, help="Evaluation method (self-refinement, peer-review, simulation)")
    parser.add_argument('--style', type=str, help="Workflow style/voice (technical, friendly, wizardly, etc.)")
    args = parser.parse_args()

    purpose = args.purpose or input("Enter the workflow purpose: ").strip()
    audience = args.audience or input("Enter target audience (e.g., beginner, expert): ").strip()
    delivery_mode = args.delivery_mode or input("Enter delivery modes (comma-separated, e.g., text,code): ")
    expansion_mode = args.expansion_mode or input("Enter expansion modes (comma-separated, e.g., recursive,modular): ")
    evaluation_method = args.evaluation_method or input("Enter evaluation method (self-refinement, peer-review, simulation): ").strip()
    style = args.style or input("Enter workflow style/voice (technical, friendly, wizardly, etc.): ").strip()

    user_params = {
        "purpose": purpose,
        "target_audience": audience,
        "delivery_mode": [mode.strip() for mode in delivery_mode.split(",")],
        "expansion_mode": [mode.strip() for mode in expansion_mode.split(",")],
        "evaluation_method": evaluation_method,
        "style": style,
    }
    return user_params

def create_workflow(user_params):
    workflow_id = generate_workflow_id()
    log(f"Initializing workflow {workflow_id} for purpose: {user_params['purpose']}")
    workflow = Workflow(
        workflow_id=workflow_id,
        purpose=user_params['purpose'],
        target_audience=user_params['target_audience'],
        delivery_mode=user_params['delivery_mode'],
        expansion_mode=user_params['expansion_mode'],
        evaluation_method=user_params['evaluation_method'],
        style=user_params['style']
    )
    workflow.run_phase_1()
    workflow.run_phase_1_5()
    workflow.run_phase_2()
    workflow.run_phase_3()
    workflow.run_phase_4()
    workflow.run_phase_5()

    # Recursive expansion phase
    expanded_dict = {
        "workflow_id": workflow.workflow_id,
        "objective": workflow.objective,
        "stages": workflow.structured_instruction,
        "modules": workflow.modular_workflow
    }
    workflow.improved_workflow = recursive_expand(expanded_dict)

    return workflow

def export_workflow(workflow):
    log(f"Exporting workflow {workflow.workflow_id}...")
    export_markdown(workflow)
    export_json(workflow)
    # Export recursive improved workflow if available
    if hasattr(workflow, "improved_workflow") and workflow.improved_workflow:
        export_markdown_dict(workflow.improved_workflow)
        export_json_dict(workflow.improved_workflow)
    log(f"Workflow {workflow.workflow_id} successfully exported!")

def export_markdown_dict(workflow_dict):
    md_content = f"# Workflow {workflow_dict['workflow_id']}\n\nObjective: {workflow_dict['objective']}\n\n"
    md_content += "## Stages\n"
    for stage, steps in workflow_dict['stages'].items():
        md_content += f"### {stage}\n"
        for step in steps:
            md_content += f"- {step}\n"
    md_content += "\n## Modules\n"
    md_content += f"{str(workflow_dict['modules']['modules'])}\n"
    md_content += "\n## Dependencies\n"
    for dep in workflow_dict['modules']['dependencies']:
        md_content += f"- {dep}\n"
    md_content += "\n## Evaluation Report\n"
    for k, v in workflow_dict.get("evaluation_report", {}).items():
        md_content += f"- {k.capitalize()}: {v}\n"
    filename = f"{workflow_dict['workflow_id']}.md"
    with open(f"templates/{filename}", "w") as f:
        f.write(md_content)

def export_json_dict(workflow_dict):
    import json
    filename = f"{workflow_dict['workflow_id']}.json"
    with open(f"templates/{filename}", "w") as f:
        json.dump(workflow_dict, f, indent=4)

def main():
    user_params = parse_user_input()
    workflow = create_workflow(user_params)
    export_workflow(workflow)
    print("\nWorkflow generation complete!")
    print(f"Markdown and JSON files saved for workflow ID: {workflow.workflow_id}")

if __name__ == "__main__":
    main()