#!/usr/bin/env python3
"""Enforce lowercase casing rules for sswg/mvm contract files."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

TARGETS = [
    "sswg.yaml",
    "mvm.yaml",
    "execution_policy.yaml",
    "governance.yaml",
    "invariants.yaml",
    "root_contract.yaml",
    "ai_system_prompt.txt",
]

DISALLOWED_UPPER = [re.compile(r"\bSSWG\b"), re.compile(r"\bMVM\b")]
LOWERCASE_TERMS = ["configs", "repos", "workflows", "schemas", "tooling"]


def lint_file(path: Path) -> list[str]:
    violations: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()

    for line_number, line in enumerate(lines, start=1):
        for pattern in DISALLOWED_UPPER:
            if pattern.search(line):
                violations.append(
                    f"{path.name}:{line_number}: disallowed uppercase term '{pattern.pattern}'"
                )

        for term in LOWERCASE_TERMS:
            for match in re.finditer(rf"\b{term}\b", line, flags=re.IGNORECASE):
                if match.group(0) != term:
                    violations.append(
                        f"{path.name}:{line_number}: '{match.group(0)}' must be lowercase '{term}'"
                    )

    return violations


def main() -> int:
    failures: list[str] = []

    for target in TARGETS:
        path = ROOT_DIR / target
        if not path.exists():
            failures.append(f"missing file: {target}")
            continue
        failures.extend(lint_file(path))

    if failures:
        print("casing lint failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("casing lint passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
