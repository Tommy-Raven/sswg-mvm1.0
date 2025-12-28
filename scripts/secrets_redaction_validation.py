from __future__ import annotations

import argparse
from pathlib import Path

from generator.failure_emitter import FailureEmitter, FailureLabel
from generator.secret_scanner import load_allowlist, scan_paths


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan repo artifacts for secret exposure."
    )
    parser.add_argument(
        "--scan-dirs",
        type=Path,
        nargs="+",
        default=[Path("artifacts"), Path("data"), Path("docs"), Path("overlays")],
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
        default=Path("governance/secret_allowlist.json"),
        help="Allowlist path for scoped secret exceptions.",
    )
    parser.add_argument(
        "--run-id", type=str, default="secrets-scan", help="Run identifier."
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/redaction/failures"))
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
