from __future__ import annotations

import argparse
import json
from pathlib import Path

from generator.determinism import (
    bijectivity_check,
    replay_determinism_check,
    write_bijectivity_report,
    write_determinism_report,
)
from generator.failure_emitter import FailureEmitter


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run determinism replay harness.")
    parser.add_argument(
        "--phase-outputs",
        type=Path,
        required=True,
        help="JSON file containing phase outputs mapping.",
    )
    parser.add_argument(
        "--measurement-ids",
        type=Path,
        required=False,
        help="JSON file with measurement identifier list.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/determinism/determinism_report.json"),
        help="Output path for determinism report.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="local-run",
        help="Run identifier for determinism report.",
    )
    parser.add_argument(
        "--inject-phase",
        type=str,
        default=None,
        help="Phase id to inject nondeterminism into for testing.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    phase_outputs = json.loads(args.phase_outputs.read_text(encoding="utf-8"))
    required_phases = ["normalize", "analyze", "validate", "compare"]
    failure, report = replay_determinism_check(
        run_id=args.run_id,
        phase_outputs=phase_outputs,
        required_phases=required_phases,
        inject_phase=args.inject_phase,
    )
    if args.measurement_ids:
        ids_payload = json.loads(args.measurement_ids.read_text(encoding="utf-8"))
        ids = ids_payload.get("ids", [])
        id_failure = bijectivity_check(ids)
        write_bijectivity_report(
            Path("artifacts/determinism/bijectivity_report.json"),
            ids,
            id_failure,
        )
        if id_failure:
            FailureEmitter(Path("artifacts/failures")).emit(id_failure, run_id=args.run_id)
            print(f"Bijectivity check failed: {id_failure.as_dict()}")
            return 1
    write_determinism_report(args.output, report)
    if failure:
        FailureEmitter(Path("artifacts/failures")).emit(failure, run_id=args.run_id)
        print(f"Determinism failure: {failure.as_dict()}")
        return 1
    print(f"Determinism replay passed: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
