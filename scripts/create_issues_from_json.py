#!/usr/bin/env python3
"""
Create GitHub issues from issues.json using gh CLI.

Usage:
  1) Ensure gh is installed and authenticated:
       gh auth login

  2) Place issues.json at the repo root (same dir as .git).

  3) From the repo root, run:
       python scripts/create_issues_from_json.py
     or:
       python scripts/create_issues_from_json.py --dry-run
"""

import argparse
import json
from pathlib import Path
from subprocess import CalledProcessError, run as subprocess_run
from typing import Any, Dict, List


def load_issues(json_path: Path) -> List[Dict[str, Any]]:
    """Load issues from issues.json; fail fast if file is missing or invalid."""
    if not json_path.exists():
        raise FileNotFoundError(f"issues.json not found at: {json_path}")
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("issues.json must contain a top-level JSON array.")
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Issue #{i} is not an object.")
        if "title" not in item or "body" not in item:
            raise ValueError(f"Issue #{i} missing required fields 'title' or 'body'.")
    return data


def build_gh_command(issue: Dict[str, Any]) -> List[str]:
    """Build gh issue create command for a single issue."""
    title = issue["title"]
    body = issue["body"]
    labels = issue.get("labels", [])

    cmd: List[str] = [
        "gh",
        "issue",
        "create",
        "--title",
        title,
        "--body",
        body,
    ]

    if labels:
        # gh accepts comma-separated labels
        cmd.extend(["--label", ",".join(labels)])

    return cmd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create GitHub issues from issues.json via gh CLI."
    )
    parser.add_argument(
        "--issues-file",
        type=str,
        default="issues.json",
        help="Path to issues JSON file (default: issues.json at repo root).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands instead of executing them.",
    )
    args = parser.parse_args()

    repo_root = Path(".").resolve()
    issues_path = (repo_root / args.issues_file).resolve()

    issues = load_issues(issues_path)

    for idx, issue in enumerate(issues, start=1):
        cmd = build_gh_command(issue)
        print(f"\n[{idx}/{len(issues)}] Creating issue: {issue['title']}")
        if args.dry_run:
            print("  DRY RUN:", " ".join(repr(c) for c in cmd))
            continue

        # Important: this relies on current directory being the correct repo
        # or gh having a default repo set (gh repo set-default).
        try:
            subprocess_run(cmd, check=True)  # nosec B603
        except CalledProcessError as exc:
            print(f"  ERROR creating issue #{idx}: {exc}")
            # Decide whether to continue or abort; here we continue.
            continue

    print("\nDone. If you used --dry-run, re-run without it to actually create issues.")


if __name__ == "__main__":
    main()
