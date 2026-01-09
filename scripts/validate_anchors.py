from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_cores.cli_arg_parser_core import build_parser, parse_args
from ai_cores.governance_core import validate_canonical_header_format
from generator.anchor_registry import AnchorRegistry, enforce_anchor
from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Validate canonical anchors.")
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
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root for governance header validation.",
    )
    return parse_args(parser)


def main() -> int:
    args = _parse_args()
    _, header_errors = validate_canonical_header_format(args.repo_root.resolve())
    if header_errors:
        failure = FailureLabel(
            Type="invalid_canonical_header",
            message=header_errors[0],
            phase_id="governance_anchor_integrity",
            path=str(args.repo_root / "directive_core" / "docs"),
        )
        FailureEmitter(Path("artifacts/failures")).emit(failure, run_id=args.run_id)
        print(header_errors[0])
        return 1
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
