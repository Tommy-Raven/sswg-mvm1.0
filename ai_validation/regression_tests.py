#!/usr/bin/env python3
"""
ai_validation/regression_tests.py — Minimal regression harness for SSWG MVM.

Purpose:
- Quickly verify that canonical workflow JSON files still pass schema validation.
- Provide a simple CLI and importable functions that can be used by pytest
  or other test runners.

At MVM stage this is intentionally lightweight. As the project matures,
this file can gain:
- golden-output comparisons
- round-trip generator tests
- coverage / score consistency checks
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from .schema_validator import validate_workflow

# Default directory where test workflow JSON files live.
# You can adjust this path to match your actual layout.
DEFAULT_TEST_DIR = Path("tests/resources/workflows")


def find_workflow_files(base_dir: Path = DEFAULT_TEST_DIR) -> List[Path]:
    """
    Discover workflow JSON files under the given directory.

    Returns:
        A list of .json Paths.
    """
    if not base_dir.exists():
        return []
    return sorted(p for p in base_dir.rglob("*.json") if p.is_file())


def load_json(path: Path) -> Dict:
    """Load a JSON file into a Python dict."""
    return json.loads(path.read_text(encoding="utf-8"))


def run_regression_suite(base_dir: Path = DEFAULT_TEST_DIR) -> Tuple[int, int]:
    """
    Run schema validation on all workflow JSON files in base_dir.

    Returns:
        (passed, failed)
    """
    files = find_workflow_files(base_dir)
    if not files:
        print(f"[regression_tests] No workflow JSON files found in {base_dir}")
        return 0, 0

    passed = 0
    failed = 0

    print(f"[regression_tests] Found {len(files)} workflow files under {base_dir}")

    for path in files:
        wf = load_json(path)
        ok, errors = validate_workflow(wf)
        wf_id = wf.get("workflow_id", path.name)

        if ok:
            print(f"  ✓ {wf_id} ({path})")
            passed += 1
        else:
            error_count = 1 if errors else 0
            print(f"  ✗ {wf_id} ({path}) — {error_count} schema issue(s)")
            failed += 1

    print(
        f"[regression_tests] Completed: {passed} passed, {failed} failed "
        f"(dir={base_dir})"
    )
    return passed, failed


def main(argv: List[str] | None = None) -> int:
    """
    CLI entrypoint.

    Usage:
        python -m ai_validation.regression_tests
        python -m ai_validation.regression_tests path/to/custom_dir
    """
    argv = argv or sys.argv[1:]
    base_dir = Path(argv[0]) if argv else DEFAULT_TEST_DIR

    passed, failed = run_regression_suite(base_dir)

    # Example of using `passed` meaningfully:
    # if no tests ran at all, flag that explicitly
    if passed == 0 and failed == 0:
        print("[regression_tests] Warning: no regression tests were executed.")

    # Non-zero exit code if any failures
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
# -----------------------------------------------------------------------------
