from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_cores.cli_arg_parser_core import build_parser, parse_args
from generator.determinism import replay_determinism_check, write_determinism_report
from generator.failure_emitter import FailureEmitter


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Run deterministic replay gate.")
    parser.add_argument(
        "--phase-outputs",
        type=Path,
        # GOVERNANCE SOURCE REMOVED
        # Canonical governance will be resolved from directive_core/docs/
        default=None,
        help="Phase outputs fixture.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="local-run",
        help="Run identifier.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/evidence_pack/determinism_report.json"),
        help="Output path for determinism report.",
    )
    return parse_args(parser)


def main() -> int:
    args = _parse_args()
    if args.phase_outputs is None:
        print("Determinism replay gate failed: phase outputs must be supplied explicitly")
        return 1
    phase_outputs = json.loads(args.phase_outputs.read_text(encoding="utf-8"))
    failure, report = replay_determinism_check(
        run_id=args.run_id,
        phase_outputs=phase_outputs,
        required_phases=["normalize", "analyze", "validate", "compare"],
    )
    write_determinism_report(args.output, report)
    if failure:
        FailureEmitter(Path("artifacts/failures")).emit(failure, run_id=args.run_id)
        print(f"Determinism replay gate failed: {failure.as_dict()}")
        return 1

    print(f"Determinism replay gate passed: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
