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

__all__ = [
    "GOVERNANCE_FILENAME_PATTERNS",
    "GOVERNANCE_TOKEN_PATTERNS",
    "find_governance_like_files",
    "is_governance_like",
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
