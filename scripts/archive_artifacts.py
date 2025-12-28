from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from generator.anchor_registry import AnchorRegistry, enforce_anchor
from generator.failure_emitter import FailureEmitter, FailureLabel
from generator.hashing import hash_data


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Archive canonical artifacts with manifest."
    )
    parser.add_argument(
        "--artifact-paths",
        type=Path,
        nargs="+",
        required=True,
        help="Artifact paths to archive.",
    )
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=Path("artifacts/archived"),
        help="Archive output directory.",
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=Path("artifacts/archived/archival_manifest.json"),
        help="Archival manifest output path.",
    )
    parser.add_argument(
        "--anchor-registry",
        type=Path,
        default=Path("config/anchor_registry.json"),
        help="Anchor registry path.",
    )
    parser.add_argument(
        "--run-id", type=str, default="archive-run", help="Run identifier."
    )
    parser.add_argument(
        "--reason", type=str, default="retention_policy", help="Archival reason."
    )
    return parser.parse_args()


def _load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = _parse_args()
    registry = AnchorRegistry(args.anchor_registry)
    emitter = FailureEmitter(Path("artifacts/archived/failures"))

    archived_entries = []
    for artifact_path in args.artifact_paths:
        if not artifact_path.exists():
            emitter.emit(
                FailureLabel(
                    Type="io_failure",
                    message="Artifact path missing for archival",
                    phase_id="log",
                    evidence={"path": str(artifact_path)},
                ),
                run_id=args.run_id,
            )
            return 1
        payload = _load_payload(artifact_path)
        metadata = payload.get("anchor", {})
        failure = enforce_anchor(
            artifact_path=artifact_path,
            metadata=metadata,
            registry=registry,
        )
        if failure:
            emitter.emit(failure, run_id=args.run_id)
            return 1

        archived_path = args.archive_dir / artifact_path.name
        archived_path.parent.mkdir(parents=True, exist_ok=True)
        archived_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        archived_entries.append(
            {
                "original_path": str(artifact_path),
                "archived_path": str(archived_path),
                "anchor": metadata,
                "hash": hash_data(payload),
            }
        )

    manifest = {
        "anchor": {
            "anchor_id": "archival_manifest",
            "anchor_version": "1.0.0",
            "scope": "archival",
            "owner": "scripts.archive_artifacts",
            "status": "draft",
        },
        "run_id": args.run_id,
        "reason": args.reason,
        "artifacts": archived_entries,
        "inputs_hash": hash_data(archived_entries),
    }
    args.manifest_path.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Archival complete. Manifest at {args.manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
