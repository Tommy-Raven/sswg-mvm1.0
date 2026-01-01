#!/usr/bin/env python3
"""Golden-path end-to-end run for sswg mvm."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from generator.main import DEFAULT_TEMPLATE, run_mvm


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the sswg mvm golden-path end-to-end demo.",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help="Path to a workflow JSON template.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("artifacts/golden_path"),
        help="Directory for generated artifacts.",
    )
    parser.add_argument(
        "--no-refine",
        action="store_true",
        help="Disable recursive refinement to keep the run deterministic.",
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="Disable history recording.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Print a JSON preview of the final workflow.",
    )
    return parser.parse_args(argv)


def _require_files(out_dir: Path, pattern: str, label: str) -> None:
    matches = list(out_dir.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"Missing {label} artifacts in {out_dir}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    refined = run_mvm(
        args.template,
        out_dir=args.out_dir,
        enable_refinement=not args.no_refine,
        enable_history=not args.no_history,
        preview=args.preview,
    )

    if not refined.get("workflow_id"):
        raise ValueError("Golden-path run did not return a workflow_id")

    _require_files(args.out_dir, "*.json", "json")
    _require_files(args.out_dir, "*.md", "markdown")
    _require_files(args.out_dir, "*.dot", "graphviz")
    return 0


if __name__ == "__main__":
    sys.exit(main())
