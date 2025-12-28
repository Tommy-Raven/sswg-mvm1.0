from __future__ import annotations

import argparse
from pathlib import Path

from generator.environment import check_environment_drift
from generator.failure_emitter import FailureEmitter


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check environment drift against dependency lock."
    )
    parser.add_argument(
        "--lock-path",
        type=Path,
        default=Path("reproducibility/dependency_lock.json"),
        help="Dependency lock path.",
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
    failure = check_environment_drift(args.lock_path)
    if failure:
        FailureEmitter(Path("artifacts/failures")).emit(failure, run_id=args.run_id)
        print(f"Environment drift detected: {failure.as_dict()}")
        return 1

    print("Environment drift check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
