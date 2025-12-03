#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai_core/cli.py — Command-line entrypoint for core orchestration.

Author: Tommy Raven, Raven Recordings, LLC ©2025

This CLI is intentionally minimal at the MVM stage. It:
- Loads a workflow JSON file.
- Wraps it in an ai_core.Workflow instance.
- Constructs a ModuleRegistry and Orchestrator.
- Runs the orchestrator across its configured phases.

For end-to-end generation / validation / export, prefer the higher-level
`generator/main.py` entrypoint. This CLI is oriented toward testing and
developing the core orchestration layer in isolation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .workflow import Workflow
from .module_registry import ModuleRegistry
from .orchestrator import Orchestrator


def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ai_core orchestration CLI (MVM)"
    )
    parser.add_argument(
        "-j",
        "--workflow-json",
        type=Path,
        required=True,
        help="Path to a schema-aligned workflow JSON file.",
    )
    parser.add_argument(
        "--phase",
        action="append",
        dest="phases",
        help=(
            "Restrict execution to specific phase(s). "
            "May be provided multiple times."
        ),
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print ai_core version and exit.",
    )
    return parser.parse_args(argv)


def load_workflow_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Workflow JSON not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: Optional[list] = None) -> int:
    from . import get_version  # local import to avoid cycles at import time

    args = parse_args(argv)

    if args.version:
        print(f"ai_core version: {get_version()}")
        return 0

    wf_data = load_workflow_json(args.workflow_json)
    workflow = Workflow(wf_data)

    # In MVM, ModuleRegistry may be sparsely populated or populated in tests.
    registry = ModuleRegistry()

    # Orchestrator is responsible for interpreting phases + executing modules.
    orchestrator = Orchestrator(module_registry=registry)

    # If phases are provided, the orchestrator should accept a subset;
    # at MVM this can be a hint the implementation can ignore.
    orchestrator.run(workflow, phases=args.phases)

    # Optional: print a short summary
    print(f"Workflow {workflow.id} executed via ai_core.Orchestrator.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# ----------------------------------------------------------------------