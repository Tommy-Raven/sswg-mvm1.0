from __future__ import annotations

import argparse
from pathlib import Path

from ai_cores.cli_arg_parser_core import build_parser, parse_args
from ai_cores.governance_core import (
    CANONICAL_GOVERNANCE_ORDER,
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
        Type="governance_violation",
        message=message,
        phase_id="governance_ingestion_order",
        path=str(path) if path else None,
    )
    FailureEmitter(Path("artifacts/governance/failures")).emit(failure, run_id=run_id)


def main() -> int:
    args = _parse_args()
    repo_root = args.repo_root.resolve()
    docs_root = repo_root / "directive_core" / "docs"

    errors = validate_governance_ingestion_order(repo_root)
    if errors:
        first_error = errors[0]
        filename = first_error.split(":")[0]
        path = docs_root / filename if filename.endswith(".md") else docs_root
        _emit_failure(
            args.run_id,
            f"Governance ingestion order validation failed: {first_error}",
            path,
        )
        print(f"Governance ingestion order failed: {first_error}")
        return 1

    print("Governance ingestion order validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
