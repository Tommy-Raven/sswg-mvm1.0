from __future__ import annotations

import argparse
import json
from pathlib import Path

from cli.cli_arg_parser_core import build_parser, parse_args
from generator.anchor_registry import AnchorRegistry
from generator.hashing import hash_data


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Generate overlay chain manifest.")
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("config/anchor_registry.json"),
        help="Anchor registry path.",
    )
    parser.add_argument(
        "--overlays-dir",
        type=Path,
        default=Path("overlays"),
        help="Directory containing overlay descriptors.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/overlays/overlay_chain_manifest.json"),
        help="Output path for overlay chain manifest.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="local-run",
        help="Run identifier.",
    )
    return parse_args(parser)


def main() -> int:
    args = _parse_args()
    registry = AnchorRegistry(args.registry)
    registry_data = registry.load()
    overlays = []
    if args.overlays_dir.exists():
        overlays = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(args.overlays_dir.glob("*.json"))
        ]
    payload = {
        "anchor": {
            "anchor_id": "overlay_chain_manifest",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "scripts.generate_overlay_chain_manifest",
            "status": "draft",
        },
        "run_id": args.run_id,
        "registry_snapshot": registry_data,
        "overlays": overlays,
    }
    payload["inputs_hash"] = hash_data(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote overlay chain manifest: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
