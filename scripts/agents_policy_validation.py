from __future__ import annotations

import argparse
from pathlib import Path

from ai_cores.cli_arg_parser_core import build_parser, parse_args
from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Validate agent policy compliance.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root for policy checks.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="policy-validate",
        help="Run identifier.",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["qa-readonly", "edit-permitted"],
        default="edit-permitted",
        help="Repository mode for write enforcement.",
    )
    parser.add_argument(
        "--commands-file",
        type=Path,
        help="Optional file containing executed commands to validate.",
    )
    return parse_args(parser)


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/policy/failures"))

    # GOVERNANCE SOURCE REMOVED
    # Canonical governance will be resolved from directive_core/docs/
    emitter.emit(
        FailureLabel(
            Type="tool_mismatch",
            message="Governance source removed: agent policy validation is disabled",
            phase_id="validate",
            evidence={"repo_root": str(args.repo_root)},
        ),
        run_id=args.run_id,
    )
    print("Agents policy validation failed")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
