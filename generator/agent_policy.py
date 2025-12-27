"""Utilities for enforcing agent policy rules and manifests."""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from generator.hashing import hash_data


PROHIBITED_COMMANDS = (
    "ls -R",
    "grep -R",
)


@dataclass(frozen=True)
class PolicyState:
    """Snapshot of policy-related metadata for a repository."""

    repo_mode: str
    agents_paths: list[str]
    policy_hash: str


def _hash_text(value: str) -> str:
    """Hash a text payload using SHA-256."""
    payload = value.encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def list_agents_paths(repo_root: Path) -> list[Path]:
    """Return all AGENTS.md paths under the repository root."""
    return sorted(repo_root.rglob("AGENTS.md"))


def build_policy_hash(agents_paths: Iterable[Path]) -> str:
    """Build a stable policy hash from the discovered AGENTS.md files."""
    entries = []
    for path in agents_paths:
        entries.append(
            {
                "path": str(path),
                "content_hash": _hash_text(path.read_text(encoding="utf-8")),
            }
        )
    return hash_data(entries)


def parse_command(command: str) -> list[str]:
    """Split a command string into executable and arguments."""
    return [part for part in command.strip().split() if part]


def is_prohibited_command(command: str) -> bool:
    """Return True when a command violates the policy rules."""
    parts = parse_command(command)
    if not parts:
        return False
    executable = parts[0]
    args = parts[1:]
    if executable in {"ls", "grep"} and "-R" in args:
        return True
    return False


def find_prohibited_commands(commands: Iterable[str]) -> list[str]:
    """Filter a list of commands down to prohibited entries."""
    return [command for command in commands if is_prohibited_command(command)]


def detect_working_tree_changes(repo_root: Path) -> list[str]:
    """Return porcelain status lines for modified files under the repo."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip()
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def build_policy_manifest(
    policy: PolicyState,
    *,
    effective_scope: Path,
    prohibited_commands: Iterable[str] = PROHIBITED_COMMANDS,
) -> dict:
    """Build a policy manifest payload with anchor metadata."""
    return {
        "anchor": {
            "anchor_id": "policy_manifest",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "generator.agent_policy",
            "status": "draft",
        },
        "effective_agents_scope": str(effective_scope),
        "policy_hash": policy.policy_hash,
        "prohibited_commands": list(prohibited_commands),
        "repo_mode": policy.repo_mode,
        "agents_paths": policy.agents_paths,
    }


def policy_state(repo_root: Path, repo_mode: str) -> PolicyState:
    """Compute the policy state for the current repository tree."""
    agents_paths = list_agents_paths(repo_root)
    return PolicyState(
        repo_mode=repo_mode,
        agents_paths=[str(path) for path in agents_paths],
        policy_hash=build_policy_hash(agents_paths),
    )


def read_commands_from_file(commands_file: Optional[Path]) -> list[str]:
    """Load command entries from a text file if it exists."""
    if commands_file is None or not commands_file.exists():
        return []
    return [
        line.strip()
        for line in commands_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
