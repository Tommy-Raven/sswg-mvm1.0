from __future__ import annotations

import argparse
from pathlib import Path

from ai_cores.cli_arg_parser_core import build_parser, parse_args
from ai_cores.governance_core import validate_governance_source_location
from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Validate governance document source locations.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root to scan.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="governance-source-validation",
        help="Run identifier.",
    )
    return parse_args(parser)


def main() -> int:
    args = _parse_args()
    repo_root = args.repo_root
    violations = validate_governance_source_location(repo_root)
    if violations:
        failure = FailureLabel(
            Type="governance_source_violation",
            message="Governance-like document found outside directive_core/",
            phase_id="governance_source_validation",
            path=str(violations[0]),
        )
        FailureEmitter(Path("artifacts/governance/failures")).emit(
            failure, run_id=args.run_id
        )
        print("Governance source validation failed")
        return 1

    print("Governance source validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
