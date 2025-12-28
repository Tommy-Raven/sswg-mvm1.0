#!/usr/bin/env python3
"""
SSWG CLI — Canonical Implementation

Purpose:
    Scaffold for controlled repository interactions and PDL phase execution.
"""

from __future__ import annotations

import argparse
from argparse import Namespace
from pathlib import Path
from subprocess import run as subprocess_run
from typing import Sequence

from pdl.default_pdl import (
    execute_phase as pdl_execute_phase,
    load_default_phases,
    load_default_workflow_spec,
)

CANONICAL_BRANCH = "canonical"


def run(cmd: Sequence[str]) -> int:
    """
    Execute a command and return the exit code.

    Args:
        cmd: Command to execute.

    Returns:
        Exit code from the executed command.
    """
    completed = subprocess_run(cmd, check=False)  # nosec B603
    return int(completed.returncode)


def cmd_phase(args: Namespace) -> None:
    """
    Execute a PDL phase.

    Args:
        args: Parsed CLI arguments containing 'name'.
    """
    workflow_spec = load_default_workflow_spec()
    phases = load_default_phases()

    if args.name not in phases:
        available = ", ".join(sorted(phases.keys()))
        print(f"[CLI] Unknown phase: {args.name!r}")
        print(f"[CLI] Available phases: {available}")
        return

    context = {
        "workflow_spec": workflow_spec,
        "phase_definitions": phases,
    }
    print(f"[CLI] Executing PDL phase: {args.name}")
    pdl_execute_phase(args.name, context=context)


def cmd_add_artifact(args: Namespace) -> None:
    """
    Add a new artifact file (additive only).

    Args:
        args: Parsed CLI arguments containing 'path' and 'content'.
    """
    path = Path(args.path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(args.content, encoding="utf-8")

    run(["git", "add", args.path])
    run(["git", "commit", "-m", f"Add artifact: {args.path}"])
    print(f"[CLI] Artifact added and committed: {args.path}")


def cmd_fork(args: Namespace) -> None:
    """
    Create a new branch/fork from the current branch.

    Args:
        args: Parsed CLI arguments containing 'name'.
    """
    exit_code = run(["git", "checkout", "-b", args.name])
    if exit_code == 0:
        print(f"[CLI] Branch created: {args.name}")
    else:
        print(f"[CLI] Failed to create branch: {args.name} (exit={exit_code})")


def cmd_request_merge(args: Namespace) -> None:
    """
    Request merge of a branch into the canonical branch.

    Args:
        args: Parsed CLI arguments containing 'branch'.
    """
    target = CANONICAL_BRANCH
    # Best-effort merge; errors are surfaced but not hidden.
    run(["git", "checkout", target])
    exit_code = run(["git", "merge", args.branch])
    if exit_code == 0:
        print(f"[CLI] Merge completed: {args.branch} → {target}")
    else:
        print(f"[CLI] Merge failed: {args.branch} → {target} " f"(exit={exit_code})")


def build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser with all SSWG commands.

    Returns:
        Configured CLI parser.
    """
    parser = argparse.ArgumentParser(prog="sswg", description="SSWG project CLI")
    subparsers = parser.add_subparsers(dest="cmd")

    # Phase command
    phase = subparsers.add_parser(
        "phase",
        help="Execute a PDL phase from the default workflow spec",
    )
    phase.add_argument("name", help="Name of the PDL phase to execute")
    phase.set_defaults(func=cmd_phase)

    # Artifact command
    add = subparsers.add_parser(
        "add-artifact",
        help="Add a new artifact (additive only)",
    )
    add.add_argument("path", help="Path to the artifact file")
    add.add_argument("content", help="Content to write into the artifact")
    add.set_defaults(func=cmd_add_artifact)

    # Fork command
    fork = subparsers.add_parser(
        "fork",
        help="Create a new branch/fork from the current branch",
    )
    fork.add_argument("name", help="Name of the new branch")
    fork.set_defaults(func=cmd_fork)

    # Merge request command
    merge = subparsers.add_parser(
        "merge-request",
        help="Merge a branch into canonical",
    )
    merge.add_argument("branch", help="Branch name to merge")
    merge.set_defaults(func=cmd_request_merge)

    return parser


def main() -> None:
    """Parse CLI arguments and execute the selected command."""
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
