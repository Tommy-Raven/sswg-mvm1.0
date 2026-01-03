---
anchor:
  anchor_id: generator_main
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

#!/usr/bin/env python3

"""
generator/main.py — codename 'Grimoire' Version 4.5  (Merged/Unified)

AI Instructional Workflow Generator
-----------------------------------
Combines the interactive CLI and programmatic JSON builder into a single,
cohesive engine.

Features:
- Interactive or command-line argument mode
- Recursive expansion hooks
- Markdown + JSON export (pretty or minified)
- Compatible with Grimoire schema v4.5
"""

from __future__ import annotations
import os, sys, json, uuid, argparse, datetime, logging
from typing import Dict, Any, Optional

# ─── Local Imports ────────────────────────────────────────────────
from workflow import Workflow
from exporters import export_markdown, export_json
from utils import generate_workflow_id, log
from recursive_expansion import recursive_expand


# ─── Logging Setup ────────────────────────────────────────────────
logger = logging.getLogger("generator")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


# ─── Input Parsing ────────────────────────────────────────────────
def parse_user_input(argv: Optional[list] = None) -> Dict[str, Any]:
    """Parse CLI args or fall back to interactive prompts."""
    parser = argparse.ArgumentParser(description="AI Instructional Workflow Generator")
    parser.add_argument("--purpose", "-p", type=str, help="Purpose of the workflow")
    parser.add_argument("--audience", "-a", type=str, help="Target audience")
    parser.add_argument("--delivery_mode", "-d", type=str, help="Delivery modes (e.g., text,code)")
    parser.add_argument("--expansion_mode", "-x", type=str, help="Expansion modes (e.g., recursive,modular)")
    parser.add_argument("--evaluation_method", "-e", type=str, help="Evaluation method (self-refinement, peer-review)")
    parser.add_argument("--style", "-s", type=str, help="Workflow style/voice (technical, friendly, wizardly)")
    parser.add_argument("--title", "-t", type=str, default="AI Instructional Workflow Generator")
    parser.add_argument("--out", "-o", type=str, default="./build/ai_workflow_output.json", help="Output JSON path")
    parser.add_argument("--pretty", action="store_true", help="Write pretty JSON output")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting existing files")
    parser.add_argument("--version", action="store_true", help="Print version and exit")

    args = parser.parse_args(argv)

    if args.version:
        print("AI Instructional Workflow Generator v4.5.0")
        sys.exit(0)

    # Fallback interactive prompts if args missing
    def ask(val, prompt):
        return val or input(prompt).strip()

    return {
        "purpose": ask(args.purpose, "Enter the workflow purpose: "),
        "audience": ask(args.audience, "Enter target audience (e.g., beginner, expert): "),
        "delivery_mode": [m.strip() for m in (args.delivery_mode or input("Enter delivery modes (text,code): ")).split(",")],
        "expansion_mode": [m.strip() for m in (args.expansion_mode or input("Enter expansion modes (recursive,modular): ")).split(",")],
        "evaluation_method": ask(args.evaluation_method, "Enter evaluation method (self-refinement, peer-review, simulation): "),
        "style": ask(args.style, "Enter workflow style/voice (technical, friendly, wizardly): "),
        "title": args.title,
        "out_path": args.out,
        "pretty": args.pretty,
        "overwrite": args.overwrite,
    }


# ─── Workflow Assembly ────────────────────────────────────────────
def assemble_metadata(params: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    return {
        "author": "Tommy Raven",
        "created": now,
        "purpose": params["purpose"],
        "audience": params["audience"],
        "style": params["style"],
        "delivery_mode": params["delivery_mode"],
        "expansion_mode": params["expansion_mode"],
        "evaluation_method": params["evaluation_method"],
        "language": "en-US",
    }


def assemble_workflow(params: Dict[str, Any]) -> Dict[str, Any]:
    workflow_id = generate_workflow_id()
    metadata = assemble_metadata(params)

    # Create Workflow phases using Workflow class
    wf = Workflow(workflow_id, params)
    wf.run_all_phases()

    # Perform recursive expansion
    expanded = recursive_expand({
        "workflow_id": wf.workflow_id,
        "objective": wf.results.get("Phase 1 — Initialization", {}).get("objective", params["purpose"]),
        "stages": wf.results.get("Phase 2 — How-To Generation", {}),
        "modules": wf.results.get("Phase 3 — Modularization", {}),
    })

    return {
        "workflow_id": workflow_id,
        "title": params["title"],
        "metadata": metadata,
        "phases": wf.results,
        "recursive_expansion": expanded,
        "timestamp": metadata["created"],
    }


# ─── Exporters ───────────────────────────────────────────────────
def export_all(workflow: Dict[str, Any], out_path: str, pretty: bool = False, overwrite: bool = True):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    if os.path.exists(out_path) and not overwrite:
        logger.error("File exists and overwrite=False: %s", out_path)
        sys.exit(2)

    # JSON Export
    with open(out_path, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        else:
            json.dump(workflow, f, separators=(",", ":"), ensure_ascii=False)

    logger.info("Workflow JSON saved to %s", out_path)

    # Markdown export (human-readable)
    export_markdown_dict(workflow)
    logger.info("Markdown export complete.")


def export_markdown_dict(workflow_dict: Dict[str, Any]):
    md_lines = [
        f"# Workflow {workflow_dict['workflow_id']}",
        f"**Title:** {workflow_dict['title']}",
        f"**Purpose:** {workflow_dict['metadata']['purpose']}",
        "",
        "## Phases",
    ]
    for name, content in workflow_dict["phases"].items():
        md_lines.append(f"### {name}")
        md_lines.append(str(content))
    md_content = "\n".join(md_lines)

    path = f"data/templates/{workflow_dict['workflow_id']}.md"
    os.makedirs("data/templates", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(md_content)
    logger.info("Markdown saved: %s", path)


# ─── Main Entrypoint ─────────────────────────────────────────────
def main(argv: Optional[list] = None) -> int:
    params = parse_user_input(argv)
    workflow_data = assemble_workflow(params)
    export_all(workflow_data, params["out_path"], params["pretty"], params["overwrite"])

    preview = json.dumps(workflow_data, indent=2)[:800]
    print("\n--- Workflow Preview ---\n", preview, "...\n")
    logger.info("Workflow generation complete for ID: %s", workflow_data["workflow_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

