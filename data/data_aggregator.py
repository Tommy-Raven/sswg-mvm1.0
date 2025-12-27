#!/usr/bin/env python3
"""
data/data_aggregator.py — Aggregated data views for SSWG MVM.

Responsibilities (MVM-level):

- Discover template and workflow JSON files on disk.
- Load JSON content in a consistent way.
- Optionally run schema validation (workflow/template) and return summaries.
- Provide simple, importable helpers that other subsystems (CLI, docs,
  tests) can use to inspect the current repository state.

This module is intentionally lightweight: it does not mutate any data,
only reads, validates, and summarizes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from ai_validation.schema_validator import validate_template, validate_workflow

# Root data directories
TEMPLATES_DIR = Path("data/templates")
WORKFLOWS_DIR = Path("data/workflows")


@dataclass
class ValidationSummary:
    """
    Lightweight container for validation results.

    Attributes:
        path: Filesystem path to the JSON file.
        kind: 'template' or 'workflow'.
        ok: True if the file validates against its schema.
        error_count: Number of schema violations (0 if ok or schema missing).
    """

    path: Path
    kind: str
    ok: bool
    error_count: int


def _iter_json_files(root: Path) -> Iterable[Path]:
    """
    Yield all *.json files under a given root directory, recursively.

    Args:
        root: Base directory to search.

    Yields:
        Path objects for each JSON file discovered.
    """
    if not root.exists():
        return

    for path in root.rglob("*.json"):
        if path.is_file():
            yield path


def _load_json(path: Path) -> Dict[str, Any]:
    """
    Load a JSON file into a Python dict.

    Args:
        path: Path to a JSON file.

    Returns:
        Parsed JSON as a dict.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    content = path.read_text(encoding="utf-8")
    return json.loads(content)


def list_template_files() -> List[Path]:
    """
    List all template JSON files under data/templates.

    Returns:
        A sorted list of Paths.
    """
    return sorted(_iter_json_files(TEMPLATES_DIR))


def list_workflow_files() -> List[Path]:
    """
    List all workflow JSON files under data/workflows.

    Returns:
        A sorted list of Paths.
    """
    return sorted(_iter_json_files(WORKFLOWS_DIR))


def validate_template_file(path: Path) -> ValidationSummary:
    """
    Validate a single template JSON file against template_schema.json.

    Args:
        path: Path to the template JSON file.

    Returns:
        ValidationSummary describing the outcome.
    """
    obj = _load_json(path)
    ok, errors = validate_template(obj)
    error_count = len(errors or [])
    return ValidationSummary(path=path, kind="template", ok=ok, error_count=error_count)


def validate_workflow_file(path: Path) -> ValidationSummary:
    """
    Validate a single workflow JSON file against workflow_schema.json.

    Args:
        path: Path to the workflow JSON file.

    Returns:
        ValidationSummary describing the outcome.
    """
    obj = _load_json(path)
    ok, errors = validate_workflow(obj)
    error_count = 1 if errors else 0
    return ValidationSummary(path=path, kind="workflow", ok=ok, error_count=error_count)


def summarize_templates() -> Tuple[List[ValidationSummary], int]:
    """
    Run schema validation over all template JSON files.

    Returns:
        (summaries, total_errors)
        summaries: List of ValidationSummary entries, one per file.
        total_errors: Sum of error_count across all summaries.
    """
    summaries: List[ValidationSummary] = []
    total_errors = 0

    for path in list_template_files():
        summary = validate_template_file(path)
        summaries.append(summary)
        total_errors += summary.error_count

    return summaries, total_errors


def summarize_workflows() -> Tuple[List[ValidationSummary], int]:
    """
    Run schema validation over all workflow JSON files.

    Returns:
        (summaries, total_errors)
        summaries: List of ValidationSummary entries, one per file.
        total_errors: Sum of error_count across all summaries.
    """
    summaries: List[ValidationSummary] = []
    total_errors = 0

    for path in list_workflow_files():
        summary = validate_workflow_file(path)
        summaries.append(summary)
        total_errors += summary.error_count

    return summaries, total_errors


def main() -> int:
    """
    Tiny CLI entrypoint for ad-hoc inspection:

    - Prints validation status for all templates and workflows.
    - Returns non-zero exit code if any file has schema errors.
    """
    tmpl_summaries, tmpl_errors = summarize_templates()
    wf_summaries, wf_errors = summarize_workflows()

    print("=== Template Validation ===")
    for s in tmpl_summaries:
        status = "OK" if s.ok else f"FAIL ({s.error_count} error(s))"
        print(f"- [templates] {s.path}: {status}")

    print("\n=== Workflow Validation ===")
    for s in wf_summaries:
        status = "OK" if s.ok else f"FAIL ({s.error_count} error(s))"
        print(f"- [workflows] {s.path}: {status}")

    total_errors = tmpl_errors + wf_errors
    print(f"\nTotal schema errors: {total_errors}")
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
