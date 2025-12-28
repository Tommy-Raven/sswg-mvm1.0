"""Secret scanning utilities with allowlist support."""

from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from generator.sanitizer import find_secret_indicators


CANONICAL_DIRS = ("generator", "cli", "pdl", "reproducibility")


@dataclass(frozen=True)
class AllowlistEntry:  # pylint: disable=too-many-instance-attributes
    """Allowlist entry for secret scanning."""

    entry_id: str
    path_glob: str
    pattern: str
    scope: str
    expires_at: str
    approved_by: str
    approval_ref: str
    allow_on_canonical: bool


def _parse_allowlist(path: Path) -> list[AllowlistEntry]:
    """Parse allowlist entries from JSON."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = []
    for raw in payload.get("entries", []):
        entries.append(
            AllowlistEntry(
                entry_id=raw.get("entry_id", ""),
                path_glob=raw.get("path_glob", ""),
                pattern=raw.get("pattern", ""),
                scope=raw.get("scope", ""),
                expires_at=raw.get("expires_at", ""),
                approved_by=raw.get("approved_by", ""),
                approval_ref=raw.get("approval_ref", ""),
                allow_on_canonical=bool(raw.get("allow_on_canonical", False)),
            )
        )
    return entries


def _is_expired(timestamp: str) -> bool:
    """Return True when the allowlist entry has expired."""
    try:
        expires = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return True
    return expires <= datetime.now(timezone.utc)


def load_allowlist(path: Optional[Path]) -> list[AllowlistEntry]:
    """Load allowlist entries from disk if present."""
    if path is None or not path.exists():
        return []
    return _parse_allowlist(path)


def _matches_entry(
    entry: AllowlistEntry, path: Path, indicators: Iterable[str]
) -> bool:
    """Return True when a path/indicator pair matches an allowlist entry."""
    if not fnmatch.fnmatch(str(path), entry.path_glob):
        return False
    if entry.pattern and entry.pattern not in indicators:
        return False
    return True


def _is_canonical_path(path: Path) -> bool:
    """Return True when the path is in a canonical directory."""
    parts = path.parts
    return len(parts) > 0 and parts[0] in CANONICAL_DIRS


def _scan_text(content: str) -> list[str]:
    """Scan a content string for secret indicators."""
    indicators = set()
    for line in content.splitlines():
        indicators.update(find_secret_indicators(line))
    return sorted(indicators)


def scan_file(path: Path) -> list[str]:
    """Scan a single file and return secret indicators."""
    if path.name.endswith(".env"):
        return ["env_file"]
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return []
    return _scan_text(content)


def scan_paths(
    paths: Iterable[Path],
    *,
    allowlist: list[AllowlistEntry],
) -> dict:
    """Scan paths for secrets and apply allowlist rules."""
    violations = []
    allowlist_errors = []
    for entry in allowlist:
        if not entry.entry_id or not entry.path_glob:
            allowlist_errors.append(
                {"entry_id": entry.entry_id, "reason": "missing required fields"}
            )
            continue
        if not entry.approved_by or not entry.approval_ref:
            allowlist_errors.append(
                {
                    "entry_id": entry.entry_id,
                    "reason": "missing approval metadata",
                }
            )
            continue
        if _is_expired(entry.expires_at):
            allowlist_errors.append(
                {"entry_id": entry.entry_id, "reason": "allowlist entry expired"}
            )
            continue
        if entry.allow_on_canonical:
            allowlist_errors.append(
                {
                    "entry_id": entry.entry_id,
                    "reason": "allowlist cannot apply to canonical",
                }
            )
            continue

    for path in paths:
        if not path.exists():
            continue
        if path.is_dir():
            for file_path in path.rglob("*"):
                if file_path.is_dir():
                    continue
                violations.extend(
                    _scan_single_path(file_path, allowlist, allowlist_errors)
                )
        else:
            violations.extend(_scan_single_path(path, allowlist, allowlist_errors))

    return {"violations": violations, "allowlist_errors": allowlist_errors}


def _scan_single_path(
    path: Path,
    allowlist: list[AllowlistEntry],
    allowlist_errors: list[dict],
) -> list[dict]:
    """Scan a path and apply allowlist rules for violations."""
    indicators = scan_file(path)
    if not indicators:
        return []
    if _is_canonical_path(path):
        allowlist_errors.append(
            {
                "entry_id": None,
                "reason": "canonical paths cannot be allowlisted",
                "path": str(path),
            }
        )
        return [
            {
                "path": str(path),
                "indicators": indicators,
                "allowlisted": False,
            }
        ]
    for entry in allowlist:
        if _matches_entry(entry, path, indicators):
            return []
    return [
        {
            "path": str(path),
            "indicators": indicators,
            "allowlisted": False,
        }
    ]
