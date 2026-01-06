from __future__ import annotations

import argparse
from pathlib import Path

from ai_cores.cli_arg_parser_core import build_parser, parse_args
from ai_cores.deprecation_core import find_deprecation_banner_violations
from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Validate deprecated governance banners.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root path.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="deprecation-banner-validation",
        help="Run identifier.",
    )
    return parse_args(parser)


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/deprecation/failures"))

    violations = find_deprecation_banner_violations(args.repo_root)
    if violations:
        path = str(violations[0])
        emitter.emit(
            FailureLabel(
                Type="deprecation_violation",
                message="Deprecated governance file lacks required non-authoritative banner",
                phase_id="deprecation_banner_validation",
                path=path,
            ),
            run_id=args.run_id,
        )
        print("Deprecation banner validation failed")
        return 1

    print("Deprecation banner validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
