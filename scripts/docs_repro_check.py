from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from subprocess import run as subprocess_run

from generator.failure_emitter import FailureEmitter, FailureLabel


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run documentation reproducibility checks."
    )
    parser.add_argument(
        "--runbook-path",
        type=Path,
        default=Path("docs/runbook.json"),
        help="Runbook JSON path.",
    )
    parser.add_argument(
        "--run-id", type=str, default="docs-repro", help="Run identifier."
    )
    return parser.parse_args()


def _load_runbook(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/docs/failures"))

    if not args.runbook_path.exists():
        emitter.emit(
            FailureLabel(
                Type="reproducibility_failure",
                message="Runbook is missing",
                phase_id="validate",
                evidence={"path": str(args.runbook_path)},
            ),
            run_id=args.run_id,
        )
        print("Docs repro check failed")
        return 1

    runbook = _load_runbook(args.runbook_path)
    for step in runbook.get("steps", []):
        command = step.get("command")
        if not command:
            continue
        proc = subprocess_run(shlex.split(command), check=False)  # nosec B603
        if proc.returncode != 0:
            emitter.emit(
                FailureLabel(
                    Type="reproducibility_failure",
                    message="Runbook command failed",
                    phase_id="validate",
                    evidence={"command": command},
                ),
                run_id=args.run_id,
            )
            print("Docs repro check failed")
            return 1
        for expected in step.get("expected_paths", []):
            if not Path(expected).exists():
                emitter.emit(
                    FailureLabel(
                        Type="reproducibility_failure",
                        message="Runbook expected output missing",
                        phase_id="validate",
                        evidence={"path": expected},
                    ),
                    run_id=args.run_id,
                )
                print("Docs repro check failed")
                return 1

    print("Docs repro check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
