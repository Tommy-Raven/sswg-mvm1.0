from __future__ import annotations

import argparse
import json
from pathlib import Path

from generator.determinism import replay_determinism_check, write_determinism_report
from generator.failure_emitter import FailureEmitter


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic replay gate.")
    parser.add_argument(
        "--phase-outputs",
        type=Path,
        default=Path("tests/fixtures/phase_outputs.json"),
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
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
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
