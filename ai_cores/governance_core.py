#!/usr/bin/env python3
"""
ai_cores/governance_core.py — Governance document detection utilities.

Provides deterministic scanning helpers for governance-like documents.
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

import tomllib

from scripts.validate_governance_ingestion import (
    CANONICAL_GOVERNANCE_ORDER,
    GovernanceIngestionError,
    validate_canonical_header_format as enforce_canonical_header_format,
    validate_governance_ingestion_order as enforce_governance_ingestion_order,
)

__all__ = [
    "CANONICAL_GOVERNANCE_ORDER",
    "GOVERNANCE_FILENAME_PATTERNS",
    "GOVERNANCE_TOKEN_PATTERNS",
    "GovernanceDocument",
    "GovernanceLoader",
    "extract_ingestion_order",
    "find_governance_like_files",
    "is_governance_like",
    "load_canonic_ledger",
    "run_governance_validations",
    "validate_canonic_ledger",
    "validate_canonical_header_format",
    "validate_constitution_precedence",
    "validate_governance_anchor_integrity",
    "validate_governance_freeze",
    "validate_governance_ingestion_order",
    "validate_governance_source_location",
    "validate_required_governance_documents",
]

GOVERNANCE_FILENAME_PATTERNS = [
    "AGENTS.toml",
    "TERMINOLOGY.toml",
    "*CONSTITUTION*.toml",
    "*POLICY*.toml",
    "*GOVERNANCE*.toml",
    "*GUARANTEE*.toml",
    "*ARCHITECTURE*.toml",
    "*REFERENCES*.toml",
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

EXCLUDED_DIRS = {".git"}

ALLOWED_GOVERNANCE_ROOTS = (
    Path("directive_core/docs"),
    Path("directive_core/schemas"),
)

ANCHOR_REQUIRED_FIELDS = [
    "anchor_id",
    "anchor_model",
    "anchor_version",
    "scope",
    "status",
    "output_mode",
    "owner",
    "init_purpose",
    "init_authors",
]


@dataclass(frozen=True)
class GovernanceDocument:
    """Representation of a loaded governance document."""

    name: str
    path: Path
    content: str


class GovernanceLoader:
    """Deterministic loader for canonical governance documents."""

    def __init__(self, docs_root: Path, order: Iterable[str] = CANONICAL_GOVERNANCE_ORDER):
        self.docs_root = docs_root
        self.order = list(order)

    def load(self) -> Tuple[List[GovernanceDocument], List[str]]:
        errors: list[str] = []
        documents: list[GovernanceDocument] = []

        if not self.docs_root.exists():
            return [], [f"Missing governance docs root: {self.docs_root}"]

        existing_files = {path.name: path for path in self.docs_root.iterdir() if path.is_file()}
        existing_lower: dict[str, str] = {}
        for name in existing_files:
            lower = name.lower()
            if lower in existing_lower:
                errors.append(
                    "Duplicate governance document casing: "
                    f"{existing_lower[lower]} and {name}"
                )
            existing_lower[lower] = name

        for filename in self.order:
            path = self.docs_root / filename
            if not path.exists():
                casing_match = existing_lower.get(filename.lower())
                if casing_match:
                    errors.append(
                        "Governance document casing mismatch: "
                        f"expected {filename}, found {casing_match}"
                    )
                else:
                    errors.append(f"Missing governance document: {filename}")
                continue

            content = path.read_text(encoding="utf-8")
            if not content.strip():
                errors.append(f"Governance document is empty: {filename}")
                continue
            documents.append(
                GovernanceDocument(name=filename, path=path, content=content)
            )

        return documents, errors

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
    """Load the TOML anchor from a canonic ledger document."""
    text = path.read_text(encoding="utf-8")
    anchor_count = len(re.findall(r"(?m)^\[anchor\]\s*$", text))
    if anchor_count != 1:
        raise ValueError("Invalid Canonical Header")
    data = tomllib.loads(text)
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
    required = ANCHOR_REQUIRED_FIELDS
    for key in required:
        if not anchor.get(key):
            errors.append(f"Missing anchor field: {key}")
    return errors


def validate_required_governance_documents(repo_root: Path) -> Tuple[List[GovernanceDocument], List[str]]:
    """Return loaded documents and validation errors for required governance docs."""
    loader = GovernanceLoader(repo_root / "directive_core" / "docs")
    return loader.load()


def validate_governance_ingestion_order(
    repo_root: Path,
    *,
    observed_order: Optional[List[str]] = None,
) -> list[str]:
    """Return validation errors for the directive_core governance order."""
    docs_root = repo_root / "directive_core" / "docs"
    try:
        enforce_governance_ingestion_order(docs_root, CANONICAL_GOVERNANCE_ORDER)
    except GovernanceIngestionError as exc:
        return [str(exc)]
    return []


def validate_canonical_header_format(repo_root: Path) -> tuple[dict[str, dict], list[str]]:
    """Return parsed anchors and validation errors for canonical header TOML enforcement."""
    docs_root = repo_root / "directive_core" / "docs"
    try:
        anchors = enforce_canonical_header_format(docs_root, CANONICAL_GOVERNANCE_ORDER)
    except GovernanceIngestionError as exc:
        return {}, [str(exc)]
    return anchors, []


def extract_ingestion_order(text: str) -> Optional[List[str]]:
    """Extract an ingestion order list from governance text, if present."""
    lines = text.splitlines()
    trigger = "Governance documents MUST be ingested in this exact order:"
    start_index = None
    for idx, line in enumerate(lines):
        if line.strip() == trigger:
            start_index = idx
            break
    if start_index is None:
        return None

    order: list[str] = []
    for line in lines[start_index + 1 :]:
        stripped = line.strip()
        if not stripped:
            if order:
                break
            continue
        match = re.match(r"^\d+\.\s+`([^`]+)`", stripped)
        if not match:
            if order:
                break
            continue
        order.append(match.group(1))
        if len(order) >= len(CANONICAL_GOVERNANCE_ORDER):
            break
    return order or None


def validate_constitution_precedence(repo_root: Path) -> list[str]:
    """Return validation errors for constitution precedence conflicts."""
    errors: list[str] = []
    documents, doc_errors = validate_required_governance_documents(repo_root)
    if doc_errors:
        return doc_errors

    constitution = next(
        (doc for doc in documents if doc.name == "SSWG_CONSTITUTION.toml"), None
    )
    if constitution is None:
        return ["Missing governance document: SSWG_CONSTITUTION.toml"]

    constitution_order = extract_ingestion_order(constitution.content)
    if constitution_order and constitution_order != CANONICAL_GOVERNANCE_ORDER:
        errors.append("Validator ingestion order conflicts with Constitution")

    authoritative_order = constitution_order or CANONICAL_GOVERNANCE_ORDER
    for doc in documents:
        if doc.name == "SSWG_CONSTITUTION.toml":
            continue
        doc_order = extract_ingestion_order(doc.content)
        if doc_order and doc_order != authoritative_order:
            errors.append(
                f"{doc.name}: governance ingestion order conflicts with Constitution"
            )
    return errors


def validate_governance_anchor_integrity(
    repo_root: Path,
    *,
    anchors: dict[str, dict] | None = None,
) -> list[str]:
    """Return validation errors for governance anchor block integrity."""
    documents, errors = validate_required_governance_documents(repo_root)
    if errors:
        return errors

    if anchors is None:
        anchors, header_errors = validate_canonical_header_format(repo_root)
        if header_errors:
            return header_errors

    anchor_errors: list[str] = []
    for doc in documents:
        anchor = anchors.get(doc.name)
        if anchor is None:
            anchor_errors.append("Invalid Canonical Header")
            continue

        for field in ANCHOR_REQUIRED_FIELDS:
            if not anchor.get(field):
                anchor_errors.append(f"{doc.name}: missing anchor field {field}")
    return anchor_errors


def _is_excluded(path: Path, repo_root: Path) -> bool:
    try:
        relative = path.relative_to(repo_root)
    except ValueError:
        return True
    return any(part in EXCLUDED_DIRS for part in relative.parts)


def _is_allowed_governance_path(path: Path, repo_root: Path) -> bool:
    for allowed in ALLOWED_GOVERNANCE_ROOTS:
        try:
            path.relative_to(repo_root / allowed)
        except ValueError:
            continue
        return True
    return False


def find_governance_like_files(repo_root: Path) -> List[Path]:
    """Return governance-like files outside directive_core authorized roots."""
    repo_root = repo_root.resolve()
    matches: List[Path] = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if _is_excluded(path, repo_root):
            continue
        if _is_allowed_governance_path(path, repo_root):
            continue
        if _has_deprecation_banner(path):
            continue
        if is_governance_like(path):
            matches.append(path.relative_to(repo_root))
    return sorted(matches)


def validate_governance_source_location(repo_root: Path) -> list[str]:
    """Return validation errors for governance source location violations."""
    violations = find_governance_like_files(repo_root)
    if violations:
        return [str(path) for path in violations]
    return []


def _is_governance_change(path: Path) -> bool:
    normalized = path.as_posix().lstrip("./")
    return normalized.startswith("directive_core/docs/") or normalized.startswith(
        "directive_core/schemas/"
    )


def validate_governance_freeze(
    repo_root: Path,
    changed_files: Iterable[Path],
    *,
    phase2_passed: bool = False,
) -> list[str]:
    """Return validation errors when governance freeze policies are violated."""
    freeze_path = repo_root / "GOVERNANCE_FREEZE.md"
    changes = list(changed_files)
    if not freeze_path.exists():
        if any(path.as_posix().endswith("GOVERNANCE_FREEZE.md") for path in changes):
            if not phase2_passed:
                return ["Governance freeze lifted before Phase 2 tests passed"]
        return []

    governance_changes = [path for path in changes if _is_governance_change(path)]
    if governance_changes:
        return [path.as_posix() for path in governance_changes]
    return []


def run_governance_validations(
    repo_root: Path,
    *,
    changed_files: Iterable[Path] = (),
    phase2_passed: bool = False,
) -> Optional["FailureLabel"]:
    """Run governance validations fail-closed and return the first failure."""
    from generator.failure_emitter import FailureLabel

    source_errors = validate_governance_source_location(repo_root)
    if source_errors:
        return FailureLabel(
            Type="governance_source_violation",
            message="Governance-like document found outside directive_core/",
            phase_id="governance_source_validation",
            path=source_errors[0],
        )

    docs, doc_errors = validate_required_governance_documents(repo_root)
    if doc_errors:
        return FailureLabel(
            Type="missing_governance_document",
            message=doc_errors[0],
            phase_id="governance_document_presence",
        )

    anchors, canonical_header_errors = validate_canonical_header_format(repo_root)
    if canonical_header_errors:
        return FailureLabel(
            Type="governance_anchor_violation",
            message=canonical_header_errors[0],
            phase_id="governance_anchor_integrity",
        )

    ingestion_errors = validate_governance_ingestion_order(
        repo_root, observed_order=[doc.name for doc in docs]
    )
    if ingestion_errors:
        return FailureLabel(
            Type="governance_ingestion_order_violation",
            message=ingestion_errors[0],
            phase_id="governance_ingestion_order",
        )

    constitution_errors = validate_constitution_precedence(repo_root)
    if constitution_errors:
        return FailureLabel(
            Type="constitution_precedence_violation",
            message=constitution_errors[0],
            phase_id="constitution_precedence",
        )

    anchor_errors = validate_governance_anchor_integrity(repo_root, anchors=anchors)
    if anchor_errors:
        return FailureLabel(
            Type="governance_anchor_violation",
            message=anchor_errors[0],
            phase_id="governance_anchor_integrity",
        )

    freeze_errors = validate_governance_freeze(
        repo_root, changed_files, phase2_passed=phase2_passed
    )
    if freeze_errors:
        return FailureLabel(
            Type="governance_freeze_violation",
            message="Governance changes blocked by active freeze",
            phase_id="governance_freeze",
            path=freeze_errors[0],
        )
    return None
