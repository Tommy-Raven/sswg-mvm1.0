from __future__ import annotations

import argparse

from pathlib import Path

from generator.audit_bundle import build_bundle, load_audit_spec
from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build audit evidence bundle.")
    parser.add_argument(
        "--audit-spec",
        type=Path,
        default=Path("governance/audit_bundle_spec.json"),
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
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/audit/failures"))

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
    bundle_dir = args.bundle_dir / args.run_id
    build_bundle(
        spec=spec,
        run_id=args.run_id,
        bundle_dir=bundle_dir,
        manifest_path=args.manifest_path,
    )

    print("Audit bundle build passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
