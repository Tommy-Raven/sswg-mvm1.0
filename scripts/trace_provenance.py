from __future__ import annotations

import argparse
import json
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trace provenance for a run or artifact.")
    parser.add_argument(
        "--provenance-path",
        type=Path,
        default=Path("artifacts/provenance/provenance_manifest.json"),
        help="Provenance manifest path.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Run identifier to trace.",
    )
    parser.add_argument(
        "--artifact-id",
        type=str,
        default=None,
        help="Artifact anchor_id or path to trace.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if not args.provenance_path.exists():
        print(f"Provenance manifest not found: {args.provenance_path}")
        return 1

    manifest = json.loads(args.provenance_path.read_text(encoding="utf-8"))
    if args.run_id and manifest.get("run_id") != args.run_id:
        print("Run id not found in provenance manifest")
        return 1

    artifact_focus = None
    if args.artifact_id:
        for artifact in manifest.get("artifacts", []):
            anchor = artifact.get("anchor", {})
            if anchor.get("anchor_id") == args.artifact_id or artifact.get("path") == args.artifact_id:
                artifact_focus = artifact
                break
        if not artifact_focus:
            print("Artifact id not found in provenance manifest")
            return 1

    lineage = {
        "run_id": manifest.get("run_id"),
        "inputs_hash": manifest.get("inputs_hash"),
        "pdl_ref": manifest.get("pdl_ref"),
        "schemas": manifest.get("schema_refs"),
        "overlays": manifest.get("overlay_chain"),
        "phase_handlers": manifest.get("phase_handlers"),
        "artifact": artifact_focus,
    }

    print(json.dumps(lineage, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
