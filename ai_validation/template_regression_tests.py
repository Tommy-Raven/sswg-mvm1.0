#!/usr/bin/env python3
"""
ai_validation/template_regression_tests.py — Minimal template regression harness.

Purpose:
- Quickly verify that lightweight template JSON files still pass template_schema.json.
- Provide a simple CLI and importable function that can be used by pytest
  or other test runners.

This mirrors ai_validation/regression_tests.py but focuses on templates under
data/templates/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from ai_validation.schema_validator import validate_template

# Default directory where template JSON files live.
DEFAULT_TEMPLATES_DIR = Path("data/templates")

# Exact schema URI used by lightweight templates
TEMPLATE_SCHEMA_URI = (
    "https://github.com/Tommy-Raven/SSWG-mvm1.0/tree/main/schemas/template_schema.json"
)


def find_template_files(base_dir: Path = DEFAULT_TEMPLATES_DIR) -> List[Path]:
    """
    Discover candidate template JSON files under the given directory.

    Strategy:
    - Start with all *.json files under data/templates/.
    - Filtering of template vs non-template is done after loading, based on $schema.
    """
    if not base_dir.exists():
        return []
    return sorted(p for p in base_dir.glob("*.json") if p.is_file())


def load_json(path: Path) -> Dict:
    """Load a JSON file into a Python dict."""
    return json.loads(path.read_text(encoding="utf-8"))


def is_template_object(obj: Dict) -> bool:
    """
    Decide if a JSON object is a lightweight template.

    Criteria (strict):
    - $schema is exactly the template_schema.json URI.

    This avoids accidentally treating workflow-shaped JSON as templates.
    """
    schema_uri = str(obj.get("$schema", "")).strip()
    return schema_uri == TEMPLATE_SCHEMA_URI


def run_template_regression_suite(
    base_dir: Path = DEFAULT_TEMPLATES_DIR,
) -> Tuple[int, int]:
    """
    Run template schema validation on all JSON files in base_dir that
    explicitly declare the template_schema.json $schema.

    Returns:
        (passed, failed)
    """
    files = find_template_files(base_dir)
    if not files:
        print(f"[template_regression_tests] No JSON files found in {base_dir}")
        return 0, 0

    passed = 0
    failed = 0
    skipped = 0

    print(
        f"[template_regression_tests] Scanning {len(files)} JSON file(s) "
        f"under {base_dir}"
    )

    for path in files:
        obj = load_json(path)

        if not is_template_object(obj):
            print("  - SKIP (non-template or no template_schema $schema): " f"{path}")
            skipped += 1
            continue

        ok, errors = validate_template(obj)
        tpl_id = obj.get("template_id", path.name)

        if ok:
            print(f"  ✓ {tpl_id} ({path})")
            passed += 1
        else:
            print(f"  ✗ {tpl_id} ({path}) — {len(errors or [])} schema issue(s)")
            failed += 1

    print(
        "[template_regression_tests] Completed: "
        f"{passed} passed, {failed} failed, {skipped} skipped "
        f"(dir={base_dir})"
    )
    return passed, failed


def main(argv: List[str] | None = None) -> int:
    """
    CLI entrypoint.

    Usage:
        python -m ai_validation.template_regression_tests
        python -m ai_validation.template_regression_tests path/to/custom_dir
    """
    argv = argv or sys.argv[1:]
    base_dir = Path(argv[0]) if argv else DEFAULT_TEMPLATES_DIR

    _ignored_passed, failed = run_template_regression_suite(base_dir)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
