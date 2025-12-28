from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from generator.hashing import hash_data


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate artifact index for retention tracking."
    )
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=Path("artifacts"),
        help="Artifacts directory to index.",
    )
    parser.add_argument(
        "--policy-path",
        type=Path,
        default=Path("governance/artifact_retention_policy.json"),
        help="Artifact retention policy path.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path("artifacts/artifact_index.json"),
        help="Artifact index output path.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _classification_lookup(policy: dict[str, Any]) -> dict[str, str]:
    rules = policy.get("classification_rules", [])
    return {
        rule["anchor_id"]: rule["retention_class"]
        for rule in rules
        if "anchor_id" in rule
    }


def main() -> int:
    args = _parse_args()
    policy = _load_json(args.policy_path) or {}
    classification_map = _classification_lookup(policy)
    entries = []

    for path in args.artifacts_dir.rglob("*.json"):
        payload = _load_json(path)
        if not payload:
            continue
        anchor = payload.get("anchor")
        if not anchor:
            continue
        anchor_id = anchor.get("anchor_id", "")
        run_id = payload.get("run_id")
        entries.append(
            {
                "anchor_id": anchor_id,
                "anchor_version": anchor.get("anchor_version"),
                "run_id": run_id,
                "path": str(path),
                "hash": hash_data(payload),
                "retention_class": classification_map.get(anchor_id, "unclassified"),
            }
        )

    index_payload = {
        "anchor": {
            "anchor_id": "artifact_index",
            "anchor_version": "1.0.0",
            "scope": "artifact",
            "owner": "scripts.generate_artifact_index",
            "status": "draft",
        },
        "entries": entries,
    }
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(json.dumps(index_payload, indent=2), encoding="utf-8")
    print(f"Artifact index written to {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
