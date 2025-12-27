from __future__ import annotations

import argparse
import json
from pathlib import Path

from generator.anchor_registry import AnchorRegistry, enforce_anchor
from generator.failure_emitter import FailureEmitter


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate canonical anchors.")
    parser.add_argument("artifact_path", type=Path, help="Artifact JSON path.")
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("config/anchor_registry.json"),
        help="Anchor registry path.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="local-run",
        help="Run identifier for failure logs.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    artifact = json.loads(args.artifact_path.read_text(encoding="utf-8"))
    anchor = artifact.get("anchor", {})
    registry = AnchorRegistry(args.registry)
    failure = enforce_anchor(
        artifact_path=args.artifact_path,
        metadata=anchor,
        registry=registry,
    )
    if failure:
        FailureEmitter(Path("artifacts/failures")).emit(failure, run_id=args.run_id)
        print(f"Anchor enforcement failed: {failure.as_dict()}")
        return 1
    print(f"Anchor enforcement passed: {args.artifact_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
