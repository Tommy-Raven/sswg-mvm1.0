#!/usr/bin/env python3
"""
SSWG Governance Audit Runner

Purpose:
- Execute mandatory governance, determinism, and validation checks
- Fail fast on first violation
- Provide explicit, non-ambiguous output suitable for CI and manual runs

Ethos:
- Deterministic
- Fail-closed
- No suppression
"""

import subprocess
import sys
from pathlib import Path


COMMANDS = [
    {
        "name": "Python compile check",
        "cmd": ["python3", "-m", "compileall", "-q", "."],
    },
    {
        "name": "Governance source location validation",
        "cmd": ["python3", "scripts/validate_governance_source_location.py"],
    },
    {
        "name": "Governance ingestion order validation",
        "cmd": ["python3", "scripts/validate_governance_ingestion_order.py"],
    },
    {
        "name": "Governance ingestion validation",
        "cmd": ["python3", "scripts/validate_governance_ingestion.py"],
    },
    {
        "name": "Semantic ambiguity validation",
        "cmd": ["python3", "scripts/validate_semantic_ambiguity.py"],
    },
    {
        "name": "Anchor validation",
        "cmd": ["python3", "scripts/validate_anchors.py"],
    },
    {
        "name": "Phase 2 governance enforcement tests",
        "cmd": ["pytest", "tests/test_governance_phase2_enforcement.py"],
    },
    {
        "name": "Canonical TOML header tests",
        "cmd": ["pytest", "tests/test_governance_toml_headers.py"],
    },
]


def run_command(name: str, cmd: list[str]) -> None:
    print("=" * 80)
    print(f"▶ RUNNING: {name}")
    print(f"  COMMAND: {' '.join(cmd)}")
    print("-" * 80)

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print("-" * 80)
        print(f"❌ FAILURE TRIGGERED: {name}")
        print(f"❌ EXIT CODE: {result.returncode}")
        print("=" * 80)
        sys.exit(result.returncode)

    print(f"✅ PASSED: {name}")


def main() -> None:
    repo_root = Path.cwd()

    if not (repo_root / ".git").exists():
        print("❌ ERROR: This script must be run from the repository root.")
        sys.exit(1)

    print("=" * 80)
    print("SSWG GOVERNANCE AUDIT — START")
    print(f"Repository: {repo_root}")
    print("=" * 80)

    for entry in COMMANDS:
        run_command(entry["name"], entry["cmd"])

    print("=" * 80)
    print("✅ ALL GOVERNANCE CHECKS PASSED")
    print("✅ Repository is TAG-SAFE")
    print("=" * 80)


if __name__ == "__main__":
    main()
