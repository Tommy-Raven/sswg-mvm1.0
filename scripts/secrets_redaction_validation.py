from __future__ import annotations

import argparse
from pathlib import Path

from ai_cores.cli_arg_parser_core import build_parser, parse_args
from generator.failure_emitter import FailureEmitter, FailureLabel
from generator.secret_scanner import load_allowlist, scan_paths


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Scan repo artifacts for secret exposure.")
    parser.add_argument(
        "--scan-dirs",
        type=Path,
        nargs="+",
        # GOVERNANCE SOURCE REMOVED
        # Canonical governance will be resolved from directive_core/docs/
        default=None,
        help="Directories to scan for secret exposure.",
    )
    parser.add_argument(
        "--scan-files",
        type=Path,
        nargs="*",
        default=[Path("config/anchor_registry.json")],
        help="Additional files to scan for secret exposure.",
    )
    parser.add_argument(
        "--allowlist-path",
        type=Path,
        # GOVERNANCE SOURCE REMOVED
        # Canonical governance will be resolved from directive_core/docs/
        default=None,
        help="Allowlist path for scoped secret exceptions.",
    )
    parser.add_argument(
        "--run-id", type=str, default="secrets-scan", help="Run identifier."
    )
    return parse_args(parser)


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/redaction/failures"))
    if args.scan_dirs is None or args.allowlist_path is None:
        emitter.emit(
            FailureLabel(
                Type="io_failure",
                message="Governance source removed: required paths must be supplied explicitly",
                phase_id="validate",
                evidence={
                    "scan_dirs": str(args.scan_dirs),
                    "allowlist_path": str(args.allowlist_path),
                },
            ),
            run_id=args.run_id,
        )
        print("Secrets redaction validation failed")
        return 1
    allowlist = load_allowlist(args.allowlist_path)
    scan_targets = list(args.scan_dirs) + list(args.scan_files)

    results = scan_paths(scan_targets, allowlist=allowlist)
    violations = results["violations"]
    allowlist_errors = results["allowlist_errors"]

    if violations or allowlist_errors:
        emitter.emit(
            FailureLabel(
                Type="reproducibility_failure",
                message="Secret scanning gate detected sensitive content",
                phase_id="validate",
                evidence={
                    "violations": violations,
                    "allowlist_errors": allowlist_errors,
                },
            ),
            run_id=args.run_id,
        )
        print("Secrets redaction validation failed")
        return 1

    print("Secrets redaction validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
