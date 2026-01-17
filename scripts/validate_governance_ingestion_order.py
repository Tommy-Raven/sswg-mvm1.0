from __future__ import annotations

import argparse
from pathlib import Path

from ai_cores.cli_arg_parser_core import build_parser, parse_args
from scripts.validate_governance_ingestion import (
    CANONICAL_GOVERNANCE_ORDER,
    GovernanceIngestionError,
    validate_canonical_header_format,
    validate_governance_ingestion_order,
)
from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Validate directive_core governance ingestion order.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root to scan.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="governance-ingestion-order",
        help="Run identifier.",
    )
    return parse_args(parser)


def _emit_failure(run_id: str, message: str, path: Path | None = None) -> None:
    failure = FailureLabel(
        Type="governance_ingestion_order_violation",
        message=message,
        phase_id="governance_ingestion_order",
        path=str(path) if path else None,
    )
    FailureEmitter(Path("artifacts/governance/failures")).emit(failure, run_id=run_id)


def main() -> int:
    args = _parse_args()
    repo_root = args.repo_root.resolve()
    docs_root = repo_root / "directive_core" / "docs"

    try:
        validate_canonical_header_format(docs_root, CANONICAL_GOVERNANCE_ORDER)
        validate_governance_ingestion_order(docs_root, CANONICAL_GOVERNANCE_ORDER)
    except GovernanceIngestionError as exc:
        first_error = str(exc)
        path = docs_root
        message = (
            first_error
            if first_error == "Invalid Canonical Header"
            else f"Governance ingestion order validation failed: {first_error}"
        )
        _emit_failure(args.run_id, message, path)
        print(message)
        return 1

    print("Governance ingestion order validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
