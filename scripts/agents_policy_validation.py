from __future__ import annotations

import argparse
import json
from pathlib import Path

from generator.agent_policy import (
    build_policy_manifest,
    detect_working_tree_changes,
    find_prohibited_commands,
    list_agents_paths,
    policy_state,
    read_commands_from_file,
)
from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate AGENTS.md policy compliance."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root containing AGENTS.md.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="policy-validate",
        help="Run identifier.",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["qa-readonly", "edit-permitted"],
        default="edit-permitted",
        help="Repository mode for write enforcement.",
    )
    parser.add_argument(
        "--commands-file",
        type=Path,
        help="Optional file containing executed commands to validate.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/policy/failures"))
    repo_root = args.repo_root
    root_agents = repo_root / "AGENTS.md"

    if not root_agents.exists():
        emitter.emit(
            FailureLabel(
                Type="tool_mismatch",
                message="Root AGENTS.md missing from repository",
                phase_id="validate",
                evidence={"path": str(root_agents)},
            ),
            run_id=args.run_id,
        )
        print("Agents policy validation failed")
        return 1

    agents_paths = list_agents_paths(repo_root)
    if not agents_paths:
        emitter.emit(
            FailureLabel(
                Type="tool_mismatch",
                message="No AGENTS.md files found in repository scope",
                phase_id="validate",
                evidence={"path": str(repo_root)},
            ),
            run_id=args.run_id,
        )
        print("Agents policy validation failed")
        return 1

    commands = read_commands_from_file(args.commands_file)
    prohibited = find_prohibited_commands(commands)
    if prohibited:
        emitter.emit(
            FailureLabel(
                Type="tool_mismatch",
                message="Prohibited commands detected in agent execution",
                phase_id="validate",
                evidence={"commands": prohibited},
            ),
            run_id=args.run_id,
        )
        print("Agents policy validation failed")
        return 1

    if args.mode == "qa-readonly":
        changes = detect_working_tree_changes(repo_root)
        if changes:
            emitter.emit(
                FailureLabel(
                    Type="tool_mismatch",
                    message="QA mode forbids working tree modifications",
                    phase_id="validate",
                    evidence={"changes": changes},
                ),
                run_id=args.run_id,
            )
            print("Agents policy validation failed")
            return 1

    state = policy_state(repo_root, args.mode)
    manifest = build_policy_manifest(state, effective_scope=root_agents)
    manifest_path = Path("artifacts/policy/policy_manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("Agents policy validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
