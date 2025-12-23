#!/usr/bin/env python3

"""Command-line entrypoint for generating instructional workflows."""

import argparse
from ai_core.orchestrator import Orchestrator

def main():
    parser = argparse.ArgumentParser(description="AI Instructional Workflow CLI")
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--audience", default="General")
    args = parser.parse_args()

    orch = Orchestrator()
    wf = orch.run(vars(args))
    print("Workflow generated:", wf["workflow_id"])

if __name__ == "__main__":
    main()
