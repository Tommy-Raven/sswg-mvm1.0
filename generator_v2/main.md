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
aiwf --purpose "educational" --audience "beginner"

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
generator/main.py

AI Instructional Workflow Generator
Produces a minified JSON workflow document according to the "Grimoire" schema.
Usable as both a CLI tool and an importable module.

Example CLI:
    python -m generator.main --purpose "Teach AI to build chatbots" \
        --audience "beginners" --style "technical" \
        --out ./build/ai_workflow_output.json --pretty

Example programmatic use:
    from generator.main import generate_workflow, export_minified_json
    wf = generate_workflow({"purpose": "X", "audience": "Y", "style": "Z"})
    export_minified_json(wf, "./out.json", pretty=False)
"""

from __future__ import annotations
import json
import uuid
import datetime
import os
import argparse
import logging
from typing import Dict, Any, Optional

# Configure module logger
logger = logging.getLogger("generator")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


# -------------------------------------------------------------------------
# Schema Builders
# -------------------------------------------------------------------------

def build_metadata(user_inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Construct the metadata block for the workflow."""
    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    metadata = {
        "author": user_inputs.get("author", "Tommy Raven"),
        "created": user_inputs.get("created", now),
        "purpose": user_inputs.get(
            "purpose", "Teach AI to create instructional workflows dynamically"
        ),
        "audience": user_inputs.get("audience", "General"),
        "style": user_inputs.get("style", "Technical"),
        "language": user_inputs.get("language", "en-US"),
        "expansion_mode": user_inputs.get("expansion_mode", ["recursive", "modular"]),
        "evaluation_metrics": user_inputs.get(
            "evaluation_metrics",
            ["clarity", "coverage", "expandability", "translatability"],
        ),
    }
    return metadata


def build_phases() -> list:
    """Build canonical five-phase description used by the generator."""
    return [
        {
            "id": "P1",
            "title": "Initialization & Variable Acquisition",
            "input": ["user_prompt"],
            "output": ["objective", "audience", "context"],
            "submodules": [
                {
                    "id": "M1A",
                    "name": "ObjectiveRefinement",
                    "inputs": ["user_prompt"],
                    "outputs": ["objective"],
                    "ai_logic": "Convert abstract goals to measurable actions.",
                },
                {
                    "id": "M1B",
                    "name": "ContextMapping",
                    "inputs": ["audience"],
                    "outputs": ["context"],
                    "ai_logic": "Identify audience profile and contextual parameters.",
                },
            ],
            "expansion_hooks": ["P2"],
            "ai_task_logic": "Prompt user for intent, parse metadata, store structured context.",
            "human_actionable": "Answer initialization prompts with detailed goal statements.",
        },
        {
            "id": "P2",
            "title": "Human-Readable How-To Generation",
            "input": ["objective", "audience"],
            "output": ["structured_instruction"],
            "submodules": [
                {
                    "id": "M2A",
                    "name": "StageWriter",
                    "ai_logic": "Draft stage-by-stage how-to guide based on objective and audience.",
                },
                {
                    "id": "M2B",
                    "name": "StepDetailer",
                    "ai_logic": "Expand each stage into steps, actions, and expected outcomes.",
                },
            ],
            "expansion_hooks": ["P3"],
            "ai_task_logic": "Generate readable instructional stages with step-by-step clarity.",
            "human_actionable": "Follow generated instructions to achieve the stated objective.",
        },
        {
            "id": "P3",
            "title": "Modular Expansion & Reusability",
            "input": ["structured_instruction"],
            "output": ["modular_workflow"],
            "submodules": [
                {
                    "id": "M3A",
                    "name": "ModuleGraphBuilder",
                    "ai_logic": "Generate dependency graph for workflow modules.",
                },
                {
                    "id": "M3B",
                    "name": "DependencyResolver",
                    "ai_logic": "Detect and resolve circular or missing dependencies.",
                },
            ],
            "ai_task_logic": "Split workflow into reusable atomic modules with dependency tags.",
            "human_actionable": "Reuse or recombine generated modules for new objectives.",
        },
        {
            "id": "P4",
            "title": "Evaluation & Quality Assurance",
            "input": ["modular_workflow"],
            "output": ["evaluation_report"],
            "submodules": [
                {
                    "id": "M4A",
                    "name": "ClarityAssessor",
                    "ai_logic": "Rate instructional clarity for human readability.",
                },
                {
                    "id": "M4B",
                    "name": "CoverageTester",
                    "ai_logic": "Check completeness and logical coverage of workflow.",
                },
                {
                    "id": "M4C",
                    "name": "TranslatorValidator",
                    "ai_logic": "Test if workflow is interpretable by another AI.",
                },
            ],
            "ai_task_logic": "Run diagnostics on clarity, coverage, and AI-translatability.",
            "human_actionable": "Review evaluation summary; approve or request refinements.",
        },
        {
            "id": "P5",
            "title": "Regeneration & Evolution",
            "input": ["evaluation_report", "user_feedback"],
            "output": ["improved_workflow"],
            "submodules": [
                {
                    "id": "M5A",
                    "name": "VersionManager",
                    "ai_logic": "Track workflow versions and changes.",
                },
                {
                    "id": "M5B",
                    "name": "FeedbackIntegrator",
                    "ai_logic": "Merge human and AI feedback into improved template.",
                },
            ],
            "ai_task_logic": "Integrate feedback and regenerate optimized workflow iterations.",
            "human_actionable": "Provide detailed notes to guide refinement.",
        },
    ]


def build_dependency_graph() -> Dict[str, Any]:
    """Canonical dependency graph for the five-phase pipeline."""
    return {
        "nodes": ["P1", "P2", "P3", "P4", "P5"],
        "edges": [["P1", "P2"], ["P2", "P3"], ["P3", "P4"], ["P4", "P5"]],
    }


def assemble_workflow(user_inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Compose the full workflow data structure."""
    workflow_id = f"ai_instructional_workflow_{uuid.uuid4().hex[:8]}"
    return {
        "workflow_id": workflow_id,
        "version": user_inputs.get("version", "3.0"),
        "title": user_inputs.get("title", "AI Instructional Workflow Generator"),
        "metadata": build_metadata(user_inputs),
        "phases": build_phases(),
        "dependency_graph": build_dependency_graph(),
        "versioning": {
            "parent_id": user_inputs.get("parent_id"),
            "child_workflows": user_inputs.get("child_workflows", []),
            "auto_regeneration": user_inputs.get("auto_regeneration", True),
        },
    }


# -------------------------------------------------------------------------
# IO / Export Helpers
# -------------------------------------------------------------------------

def export_minified_json(
    data: Dict[str, Any],
    out_path: str,
    pretty: bool = False,
    overwrite: bool = True,
) -> str:
    """Write JSON to out_path. If pretty==False, writes minified JSON."""
    if not out_path:
        raise ValueError("out_path must be provided")

    out_dir = os.path.dirname(os.path.abspath(out_path)) or "."
    os.makedirs(out_dir, exist_ok=True)

    if os.path.exists(out_path) and not overwrite:
        raise FileExistsError(f"File exists and overwrite=False: {out_path}")

    if pretty:
        serialized = json.dumps(data, indent=2, sort_keys=False, ensure_ascii=False)
    else:
        serialized = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(serialized)

    logger.info("Workflow saved to %s", out_path)
    return out_path


# -------------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------------

def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="generator.main", description="AI Instructional Workflow Generator"
    )
    parser.add_argument("--purpose", "-p", type=str, help="Workflow purpose/goal")
    parser.add_argument("--audience", "-a", type=str, help="Target audience")
    parser.add_argument("--style", "-s", type=str, help="Writing style or voice")
    parser.add_argument(
        "--title",
        "-t",
        type=str,
        default="AI Instructional Workflow Generator",
        help="Title of the workflow",
    )
    parser.add_argument(
        "--out",
        "-o",
        type=str,
        default="./build/ai_workflow_output.json",
        help="Output JSON path",
    )
    parser.add_argument("--pretty", action="store_true", help="Write pretty-printed JSON")
    parser.add_argument(
        "--overwrite", action="store_true", help="Allow overwriting the output file"
    )
    parser.add_argument(
        "--version", dest="version_flag", action="store_true", help="Print module version"
    )
    return parser.parse_args(argv)


def main(argv: Optional[list] = None) -> int:
    args = parse_args(argv)

    if args.version_flag:
        print("generator.main version 3.0")
        return 0

    user_inputs: Dict[str, Any] = {
        "purpose": args.purpose
        or "Teach AI to create instructional workflows dynamically",
        "audience": args.audience or "General",
        "style": args.style or "Technical",
        "title": args.title,
        "language": "en-US",
        "expansion_mode": ["recursive", "modular"],
        "evaluation_metrics": [
            "clarity",
            "coverage",
            "expandability",
            "translatability",
        ],
    }

    workflow = assemble_workflow(user_inputs)

    try:
        export_minified_json(workflow, args.out, pretty=args.pretty, overwrite=args.overwrite)
    except FileExistsError as e:
        logger.error(str(e))
        return 2
    except Exception as e:
        logger.exception("Failed to export workflow: %s", e)
        return 3

    # Show brief preview
    raw = json.dumps(workflow, separators=(",", ":")) if not args.pretty else json.dumps(workflow, indent=2)
    preview = raw[:800] + ("..." if len(raw) > 800 else "")
    print(preview)
    return 0


# -------------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------------

def generate_workflow(user_inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Public function for programmatic generation."""
    return assemble_workflow(user_inputs)


if __name__ == "__main__":
    raise SystemExit(main())
