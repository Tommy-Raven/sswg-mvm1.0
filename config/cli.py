#!/usr/bin/env python3

"""Command-line entrypoint for generating instructional workflows."""

import argparse

from ai_core.orchestrator import Orchestrator, RunContext


def main():
    parser = argparse.ArgumentParser(description="AI Instructional Workflow CLI")
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--audience", default="General")
    args = parser.parse_args()

    workflow_payload = {
        "workflow_id": f"config_cli_{args.purpose.lower().replace(' ', '_')}",
        "params": {"purpose": args.purpose, "audience": args.audience},
    }
    orchestrator = Orchestrator()
    context = RunContext(workflow_source=workflow_payload)
    result = orchestrator.run_mvm(context)
    print("Workflow generated:", result.workflow.id)


if __name__ == "__main__":
    main()
