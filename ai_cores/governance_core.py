#!/usr/bin/env python3
"""
ai_cores/governance_core.py — Governance document detection utilities.

Provides deterministic scanning helpers for governance-like documents.
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path
from typing import Iterable, List

import yaml

__all__ = [
    "CANONICAL_GOVERNANCE_ORDER",
    "GOVERNANCE_FILENAME_PATTERNS",
    "GOVERNANCE_TOKEN_PATTERNS",
    "find_governance_like_files",
    "is_governance_like",
    "load_canonic_ledger",
    "validate_canonic_ledger",
    "validate_governance_ingestion_order",
]

CANONICAL_GOVERNANCE_ORDER = [
    "TERMINOLOGY.md",
    "SSWG_CONSTITUTION.md",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "FORMAL_GUARANTEES.md",
    "REFERENCES.md",
]

GOVERNANCE_FILENAME_PATTERNS = [
    "AGENTS.md",
    "TERMINOLOGY.md",
    "*CONSTITUTION*.md",
    "*POLICY*.md",
    "*GOVERNANCE*.md",
    "*GUARANTEE*.md",
    "*ARCHITECTURE*.md",
    "*REFERENCES*.md",
]

GOVERNANCE_TOKEN_PATTERNS = [
    "MUST",
    "SHALL",
    "invariant",
    "governance",
    "validator",
    "enforcement",
    "fail_closed",
]

EXCLUDED_DIRS = {".git", "directive_core"}

DEPRECATION_BANNER_PATTERNS = [
    re.compile(r"DEPRECATED\s+—\s+NON-AUTHORITATIVE", re.IGNORECASE),
    re.compile(r"NOT canonical", re.IGNORECASE),
    re.compile(r"NEVER be used as a source of governance", re.IGNORECASE),
    re.compile(r"Canonical governance .*directive_core/docs", re.IGNORECASE),
]


def _matches_filename(name: str) -> bool:
    return any(fnmatch.fnmatch(name, pattern) for pattern in GOVERNANCE_FILENAME_PATTERNS)


def _matches_tokens(payload: str) -> bool:
    for token in GOVERNANCE_TOKEN_PATTERNS:
        if re.search(rf"\b{re.escape(token)}\b", payload, flags=re.IGNORECASE):
            return True
    return False


def is_governance_like(path: Path) -> bool:
    """Return True when the file meets governance-like criteria."""
    if _matches_filename(path.name):
        return True
    try:
        payload = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return _matches_tokens(payload)


def _has_deprecation_banner(path: Path, *, max_lines: int = 12) -> bool:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return False
    snippet = "\n".join(lines[:max_lines])
    return all(pattern.search(snippet) for pattern in DEPRECATION_BANNER_PATTERNS)


def load_canonic_ledger(path: Path) -> dict:
    """Load the YAML anchor from a canonic ledger document."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "# Canonic Ledger":
        raise ValueError("Missing canonical header")
    try:
        start = lines.index("```yaml")
        end = lines.index("```", start + 1)
    except ValueError as exc:
        raise ValueError("Missing YAML ledger block") from exc
    payload = "\n".join(lines[start + 1 : end])
    data = yaml.safe_load(payload)
    if not isinstance(data, dict) or "anchor" not in data:
        raise ValueError("Missing anchor payload")
    anchor = data["anchor"]
    if not isinstance(anchor, dict):
        raise ValueError("Malformed anchor payload")
    return anchor


def validate_canonic_ledger(path: Path) -> list[str]:
    """Return validation error messages for a canonic ledger document."""
    errors: list[str] = []
    try:
        anchor = load_canonic_ledger(path)
    except ValueError as exc:
        return [str(exc)]
    required = ["anchor_id", "anchor_model", "anchor_version", "scope", "status"]
    for key in required:
        if not anchor.get(key):
            errors.append(f"Missing anchor field: {key}")
    return errors


def validate_governance_ingestion_order(repo_root: Path) -> list[str]:
    """Return validation errors for the directive_core governance order."""
    errors: list[str] = []
    docs_root = repo_root / "directive_core" / "docs"
    for filename in CANONICAL_GOVERNANCE_ORDER:
        path = docs_root / filename
        if not path.exists():
            errors.append(f"Missing governance document: {filename}")
            continue
        ledger_errors = validate_canonic_ledger(path)
        for error in ledger_errors:
            errors.append(f"{filename}: {error}")
    return errors


def _is_excluded(path: Path, repo_root: Path) -> bool:
    try:
        relative = path.relative_to(repo_root)
    except ValueError:
        return True
    return any(part in EXCLUDED_DIRS for part in relative.parts)


def find_governance_like_files(repo_root: Path) -> List[Path]:
    """Return governance-like files outside directive_core/docs."""
    repo_root = repo_root.resolve()
    matches: List[Path] = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if _is_excluded(path, repo_root):
            continue
        if _has_deprecation_banner(path):
            continue
        if is_governance_like(path):
            matches.append(path.relative_to(repo_root))
    return sorted(matches)
