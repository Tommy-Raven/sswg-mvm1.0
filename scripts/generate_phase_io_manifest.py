from __future__ import annotations

import argparse
import json
from pathlib import Path

from generator.failure_emitter import FailureEmitter
from generator.phase_io import (
    build_phase_io_manifest,
    detect_phase_collapse,
    load_pdl,
    write_manifest,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate phase IO manifest.")
    parser.add_argument("pdl_path", type=Path, help="PDL YAML path.")
    parser.add_argument(
        "--observed",
        type=Path,
        default=None,
        help="Optional JSON file with observed IO per phase.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/phase_io/phase_io_manifest.json"),
        help="Output path for manifest JSON.",
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
    pdl_obj = load_pdl(args.pdl_path)
    observed = None
    if args.observed:
        observed = json.loads(args.observed.read_text(encoding="utf-8"))
    manifest = build_phase_io_manifest(pdl_obj, observed)
    failure = detect_phase_collapse(manifest, pdl_obj)
    if failure:
        FailureEmitter(Path("artifacts/failures")).emit(failure, run_id=args.run_id)
        print(f"Phase collapse detected: {failure.as_dict()}")
        return 1
    write_manifest(args.output, manifest)
    print(f"Wrote phase IO manifest: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
