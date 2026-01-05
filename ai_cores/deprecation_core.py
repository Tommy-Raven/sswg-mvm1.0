"""Core helpers for deprecated governance banner validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

__all__ = [
    "DeprecationBannerConfig",
    "find_deprecation_banner_violations",
    "iter_deprecated_files",
    "REQUIRED_BANNER_LINES",
]


REQUIRED_BANNER_LINES = [
    "> ⚠️ DEPRECATED — NON-AUTHORITATIVE",
    ">",
    "> This document is NOT canonical.",
    "> It SHALL NEVER be used as a source of governance.",
    "> Canonical governance resides exclusively in directive_core/docs/.",
    "> This file exists only for historical or migration reference.",
]


@dataclass(frozen=True)
class DeprecationBannerConfig:
    """Configuration for deprecated governance banner enforcement."""

    repo_root: Path
    target_dirs: Sequence[Path]
    max_lines: int = 20


def iter_deprecated_files(config: DeprecationBannerConfig) -> Iterable[Path]:
    """Yield deprecated governance files under configured directories."""
    for target_dir in config.target_dirs:
        if not target_dir.exists():
            continue
        for path in sorted(target_dir.rglob("*")):
            if path.is_file():
                yield path


def _has_required_banner(lines: Sequence[str]) -> bool:
    if len(lines) < len(REQUIRED_BANNER_LINES):
        return False
    return list(lines[: len(REQUIRED_BANNER_LINES)]) == REQUIRED_BANNER_LINES


def find_deprecation_banner_violations(
    repo_root: Path,
    *,
    max_lines: int = 20,
    target_dirs: Sequence[Path] | None = None,
) -> list[Path]:
    """Return relative paths missing the required deprecation banner."""
    resolved_targets = (
        [
            repo_root / "legacy_governance/deprecated",
            repo_root / "legacy_governance/migration_sources",
        ]
        if target_dirs is None
        else [repo_root / target_dir for target_dir in target_dirs]
    )
    config = DeprecationBannerConfig(
        repo_root=repo_root, target_dirs=resolved_targets, max_lines=max_lines
    )
    violations: list[Path] = []
    for path in iter_deprecated_files(config):
        lines = path.read_text(encoding="utf-8").splitlines()
        if not _has_required_banner(lines[: config.max_lines]):
            violations.append(path.relative_to(repo_root))
    return violations
