from __future__ import annotations

import argparse

from pathlib import Path

from ai_cores.cli_arg_parser_core import build_parser, parse_args
from data.outputs.audit_bundle import build_audit_bundle, load_audit_spec
from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Build audit evidence bundle.")
    parser.add_argument(
        "--audit-spec",
        type=Path,
        # GOVERNANCE SOURCE REMOVED
        # Canonical governance will be resolved from directive_core/docs/
        default=None,
        help="Audit bundle specification path.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="audit-run",
        help="Run identifier.",
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        default=Path("artifacts/audit"),
        help="Audit bundle directory.",
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=Path("artifacts/audit/audit_bundle_manifest.json"),
        help="Audit bundle manifest path.",
    )
    parser.add_argument(
        "--benchmark-log",
        type=Path,
        default=Path("artifacts/performance/benchmarks_20251227_090721.json"),
        help="Benchmark log path used for audit metrics.",
    )
    return parse_args(parser)


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/audit/failures"))
    if args.audit_spec is None:
        emitter.emit(
            FailureLabel(
                Type="io_failure",
                message="Governance source removed: audit spec path must be supplied explicitly",
                phase_id="validate",
                evidence={"audit_spec": str(args.audit_spec)},
            ),
            run_id=args.run_id,
        )
        print("Audit bundle build failed")
        return 1

    if not args.audit_spec.exists():
        emitter.emit(
            FailureLabel(
                Type="reproducibility_failure",
                message="Audit bundle spec missing",
                phase_id="validate",
                evidence={"path": str(args.audit_spec)},
            ),
            run_id=args.run_id,
        )
        print("Audit bundle build failed")
        return 1

    spec = load_audit_spec(args.audit_spec)
    if not args.benchmark_log.exists():
        emitter.emit(
            FailureLabel(
                Type="reproducibility_failure",
                message="Benchmark log missing",
                phase_id="validate",
                evidence={"path": str(args.benchmark_log)},
            ),
            run_id=args.run_id,
        )
        print("Audit bundle build failed")
        return 1

    bundle_dir = args.bundle_dir / args.run_id
    build_audit_bundle(
        spec=spec,
        run_id=args.run_id,
        bundle_dir=bundle_dir,
        manifest_path=args.manifest_path,
        benchmark_log_path=args.benchmark_log,
    )

    print("Audit bundle build passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
