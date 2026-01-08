"""Phase 2 governance enforcement tests (2.0 namespace)."""
from __future__ import annotations

from pathlib import Path

import pytest

from ai_cores.governance_core import (
    CANONICAL_GOVERNANCE_ORDER,
    run_governance_validations,
    validate_constitution_precedence,
    validate_governance_anchor_integrity,
    validate_governance_freeze,
    validate_governance_ingestion_order,
    validate_governance_source_location,
    validate_required_governance_documents,
)
from tests.assertions import require


def _make_anchor_doc(anchor_id: str, *, extra: str = "") -> str:
    return (
        "# Canonic Ledger\n"
        "```yaml\n"
        "anchor:\n"
        f'  anchor_id: "{anchor_id}"\n'
        '  anchor_model: "sswg+mvm"\n'
        '  anchor_version: "1.2.0"\n'
        '  scope: "directive_core/docs"\n'
        '  status: "invariant"\n'
        "```\n\n"
        f"{extra}"
    )


def _constitution_text(order: list[str] | None = None) -> str:
    order = order or CANONICAL_GOVERNANCE_ORDER
    order_lines = "\n".join(
        f"{index + 1}. `{name}`" for index, name in enumerate(order)
    )
    extra = (
        "## Canonical Governance Ingestion Order\n\n"
        "Governance documents MUST be ingested in this exact order:\n\n"
        f"{order_lines}\n"
    )
    return _make_anchor_doc("sswg_constitution", extra=extra)


def _write_required_docs(repo_root: Path, overrides: dict[str, str | None] | None = None) -> None:
    overrides = overrides or {}
    docs_root = repo_root / "directive_core" / "docs"
    docs_root.mkdir(parents=True, exist_ok=True)
    for name in CANONICAL_GOVERNANCE_ORDER:
        if name in overrides and overrides[name] is None:
            continue
        if name == "SSWG_CONSTITUTION.md":
            content = overrides.get(name, _constitution_text())
        else:
            content = overrides.get(
                name, _make_anchor_doc(name.lower(), extra="## Section\n")
            )
        (docs_root / name).write_text(content, encoding="utf-8")


def _repo_with_required_docs(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    _write_required_docs(repo_root)
    return repo_root


def test_governance_source_location_enforced(tmp_path: Path) -> None:
    repo_root = _repo_with_required_docs(tmp_path)
    allowed_schema = repo_root / "directive_core" / "schemas"
    allowed_schema.mkdir(parents=True, exist_ok=True)
    (allowed_schema / "governance.json").write_text("MUST", encoding="utf-8")
    require(
        not validate_governance_source_location(repo_root),
        "Expected no governance source violations inside directive_core/",
    )

    misplaced = repo_root / "docs"
    misplaced.mkdir()
    offending_path = misplaced / "GOVERNANCE.md"
    offending_path.write_text("MUST", encoding="utf-8")
    violations = validate_governance_source_location(repo_root)
    require(violations, "Expected governance source violations")
    require(
        str(offending_path.relative_to(repo_root)) in violations,
        "Expected offending path to be reported",
    )


def test_governance_ingestion_order(tmp_path: Path) -> None:
    repo_root = _repo_with_required_docs(tmp_path)
    documents, errors = validate_required_governance_documents(repo_root)
    require(not errors, f"Unexpected document errors: {errors}")
    loaded_order = [doc.name for doc in documents]
    require(
        loaded_order == CANONICAL_GOVERNANCE_ORDER,
        "Governance loader must ingest documents in canonical order",
    )
    reversed_order = list(reversed(CANONICAL_GOVERNANCE_ORDER))
    order_errors = validate_governance_ingestion_order(
        repo_root, observed_order=reversed_order
    )
    require(order_errors, "Expected ingestion order violations for wrong order")


@pytest.mark.parametrize(
    "overrides, expected_fragment",
    [
        ({"ARCHITECTURE.md": None}, "Missing governance document: ARCHITECTURE.md"),
        ({"TERMINOLOGY.md": ""}, "Governance document is empty: TERMINOLOGY.md"),
    ],
)
def test_required_governance_documents_present(
    tmp_path: Path,
    overrides: dict[str, str | None],
    expected_fragment: str,
) -> None:
    repo_root = tmp_path / "repo"
    _write_required_docs(repo_root, overrides=overrides)
    documents, errors = validate_required_governance_documents(repo_root)
    require(errors, "Expected missing governance document errors")
    require(
        expected_fragment in errors[0],
        f"Expected error fragment '{expected_fragment}', got '{errors[0]}'",
    )
    failure = run_governance_validations(repo_root)
    require(failure is not None, "Expected validator failure for missing docs")
    require(
        failure.Type == "missing_governance_document",
        "Expected missing_governance_document failure type",
    )


def test_required_governance_documents_casing(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    overrides = {"TERMINOLOGY.md": None}
    _write_required_docs(repo_root, overrides=overrides)
    docs_root = repo_root / "directive_core" / "docs"
    (docs_root / "terminology.md").write_text(
        _make_anchor_doc("terminology", extra="## Section\n"),
        encoding="utf-8",
    )
    _, errors = validate_required_governance_documents(repo_root)
    require(errors, "Expected casing mismatch errors")
    require(
        "Governance document casing mismatch" in errors[0],
        f"Expected casing mismatch error, got '{errors[0]}'",
    )


def test_constitution_precedence(tmp_path: Path) -> None:
    repo_root = _repo_with_required_docs(tmp_path)
    docs_root = repo_root / "directive_core" / "docs"
    agents_path = docs_root / "AGENTS.md"
    conflicting_order = CANONICAL_GOVERNANCE_ORDER[1:] + [
        CANONICAL_GOVERNANCE_ORDER[0]
    ]
    agents_path.write_text(
        _make_anchor_doc(
            "agents",
            extra=(
                "## Canonical Governance Ingestion Order\n\n"
                "Governance documents MUST be ingested in this exact order:\n\n"
                + "\n".join(
                    f"{index + 1}. `{name}`"
                    for index, name in enumerate(conflicting_order)
                )
                + "\n"
            ),
        ),
        encoding="utf-8",
    )
    errors = validate_constitution_precedence(repo_root)
    require(errors, "Expected constitution precedence conflict")
    require(
        "conflicts with Constitution" in errors[0],
        f"Expected constitution conflict error, got '{errors[0]}'",
    )

    (docs_root / "SSWG_CONSTITUTION.md").write_text(
        _constitution_text(order=list(reversed(CANONICAL_GOVERNANCE_ORDER))),
        encoding="utf-8",
    )
    errors = validate_constitution_precedence(repo_root)
    require(errors, "Expected validator-constitution conflict")
    require(
        "Validator ingestion order conflicts with Constitution" in errors[0],
        "Expected constitution precedence violation for validator mismatch",
    )


def test_governance_anchor_integrity(tmp_path: Path) -> None:
    repo_root = _repo_with_required_docs(tmp_path)
    docs_root = repo_root / "directive_core" / "docs"
    architecture_path = docs_root / "ARCHITECTURE.md"
    architecture_path.write_text(
        _make_anchor_doc(
            "architecture",
            extra=(
                "```yaml\n"
                "anchor:\n"
                '  anchor_id: "duplicate"\n'
                '  anchor_model: "sswg+mvm"\n'
                '  anchor_version: "1.2.0"\n'
                '  scope: "directive_core/docs"\n'
                '  status: "invariant"\n'
                "```\n"
            ),
        ),
        encoding="utf-8",
    )
    errors = validate_governance_anchor_integrity(repo_root)
    require(errors, "Expected governance anchor violations")
    failure = run_governance_validations(repo_root)
    require(failure is not None, "Expected validator failure for anchor integrity")
    require(
        failure.Type == "governance_anchor_violation",
        "Expected governance_anchor_violation failure type",
    )


def test_validator_fail_closed_on_governance_violation(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _write_required_docs(repo_root, overrides={"ARCHITECTURE.md": None})
    misplaced = repo_root / "schemas"
    misplaced.mkdir(parents=True)
    (misplaced / "governance.md").write_text("MUST", encoding="utf-8")
    failure = run_governance_validations(repo_root)
    require(failure is not None, "Expected governance validator failure")
    require(
        failure.Type == "governance_source_violation",
        "Expected governance_source_violation to fail closed first",
    )
    exit_code = 1 if failure else 0
    require(exit_code != 0, "Expected non-zero exit code on governance violation")


def test_governance_freeze_enforced(tmp_path: Path) -> None:
    repo_root = _repo_with_required_docs(tmp_path)
    (repo_root / "GOVERNANCE_FREEZE.md").write_text("freeze", encoding="utf-8")
    changed_files = [Path("directive_core/docs/AGENTS.md")]
    errors = validate_governance_freeze(repo_root, changed_files)
    require(errors, "Expected governance freeze violations")

    (repo_root / "GOVERNANCE_FREEZE.md").unlink()
    lift_errors = validate_governance_freeze(
        repo_root,
        [Path("GOVERNANCE_FREEZE.md")],
        phase2_passed=False,
    )
    require(lift_errors, "Expected governance freeze lift violation before Phase 2 pass")
