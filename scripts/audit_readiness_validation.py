from __future__ import annotations

import argparse
import json
from pathlib import Path

from generator.audit_bundle import validate_bundle
from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate audit bundle readiness.")
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=Path("artifacts/audit/audit_bundle_manifest.json"),
        help="Audit bundle manifest path.",
    )
    parser.add_argument(
        "--certificate-path",
        type=Path,
        default=Path("artifacts/audit/audit_certificate.json"),
        help="Audit certificate output path.",
    )
    parser.add_argument(
        "--run-id", type=str, default="audit-validate", help="Run identifier."
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/audit/failures"))

    if not args.manifest_path.exists():
        emitter.emit(
            FailureLabel(
                Type="reproducibility_failure",
                message="Audit bundle manifest missing",
                phase_id="validate",
                evidence={"path": str(args.manifest_path)},
            ),
            run_id=args.run_id,
        )
        print("Audit readiness validation failed")
        return 1

    manifest = json.loads(args.manifest_path.read_text(encoding="utf-8"))
    results = validate_bundle(manifest)
    if results["status"] != "pass":
        emitter.emit(
            FailureLabel(
                Type="reproducibility_failure",
                message="Audit bundle validation failed",
                phase_id="validate",
                evidence={"errors": results.get("errors", [])},
            ),
            run_id=args.run_id,
        )
        print("Audit readiness validation failed")
        return 1

    certificate = {
        "anchor": {
            "anchor_id": "audit_certificate",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "scripts.audit_readiness_validation",
            "status": "draft",
        },
        "run_id": manifest.get("run_id"),
        "bundle_hash": manifest.get("bundle_hash"),
        "coverage": {
            "bundle_complete": True,
            "hash_integrity": True,
            "consistency_checks": True,
        },
        "gating_summary": {
            "audit_readiness_validation": "pass",
        },
    }
    args.certificate_path.parent.mkdir(parents=True, exist_ok=True)
    args.certificate_path.write_text(
        json.dumps(certificate, indent=2), encoding="utf-8"
    )

    print("Audit readiness validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
