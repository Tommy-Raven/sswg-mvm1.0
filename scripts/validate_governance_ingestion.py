from __future__ import annotations

from pathlib import Path
import re
import tomllib

CANONICAL_GOVERNANCE_ORDER = [
    "TERMINOLOGY.toml",
    "AGENTS.toml",
    "SSWG_CONSTITUTION.toml",
    "SECURITY_INVARIANTS.toml",
    "FORMAT_BOUNDARY_CONTRACT.toml",
    "ARCHITECTURE.toml",
    "FORMAL_GUARANTEES.toml",
    "REFERENCES.toml",
    "deprecated_nomenclature.toml",
]


class GovernanceIngestionError(RuntimeError):
    pass


def _extract_canonical_header(content: str) -> dict:
    anchor_count = len(re.findall(r"(?m)^\[anchor\]\s*$", content))
    if anchor_count != 1:
        raise GovernanceIngestionError("Invalid Canonical Header")

    try:
        data = tomllib.loads(content)
    except tomllib.TOMLDecodeError as exc:
        raise GovernanceIngestionError("Invalid Canonical Header") from exc
    if not isinstance(data, dict) or "anchor" not in data or not isinstance(data["anchor"], dict):
        raise GovernanceIngestionError("Invalid Canonical Header")

    anchor = data["anchor"]

    return anchor


def validate_canonical_header_format(
    docs_dir: Path,
    expected_order: list[str],
) -> dict[str, dict]:
    anchors: dict[str, dict] = {}
    for path in docs_dir.iterdir():
        if not path.is_file() or path.suffix != ".toml":
            continue
        content = path.read_text(encoding="utf-8")
        anchor = _extract_canonical_header(content)
        if path.name in expected_order:
            anchors[path.name] = anchor
    for filename in expected_order:
        path = docs_dir / filename
        if not path.exists():
            continue
    return anchors


def validate_governance_ingestion_order(
    docs_dir: Path,
    expected_order: list[str],
) -> bool:
    """
    Enforces canonical governance ingestion order.
    Fail-closed on any deviation.
    """

    if not docs_dir.exists() or not docs_dir.is_dir():
        raise GovernanceIngestionError(
            f"[governance_violation] docs directory not found: {docs_dir}"
        )

    present = sorted(
        p.name for p in docs_dir.iterdir() if p.is_file() and p.suffix == ".toml"
    )

    expected_set = set(expected_order)
    present_set = set(present)

    missing = expected_set - present_set
    if missing:
        raise GovernanceIngestionError(
            f"[governance_violation] missing governance documents: {sorted(missing)}"
        )

    present_ordered = [name for name in present if name in expected_set]

    if present_ordered != expected_order:
        raise GovernanceIngestionError(
            "[governance_violation] governance ingestion order mismatch\n"
            f"expected: {expected_order}\n"
            f"found:    {present_ordered}"
        )

    return True
