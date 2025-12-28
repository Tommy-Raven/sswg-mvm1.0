from __future__ import annotations

import argparse
import json
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate run health summary from telemetry."
    )
    parser.add_argument(
        "--telemetry-path",
        type=Path,
        default=Path("artifacts/telemetry/run_telemetry.json"),
        help="Telemetry artifact path.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path("artifacts/telemetry/run_health_summary.md"),
        help="Output summary path.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if not args.telemetry_path.exists():
        print(f"Telemetry artifact missing: {args.telemetry_path}")
        return 1

    telemetry = json.loads(args.telemetry_path.read_text(encoding="utf-8"))
    gate_results = telemetry.get("gate_results", {})
    failure_counts = telemetry.get("failure_counts", {})
    determinism_status = telemetry.get("determinism_status", {})

    summary_lines = [
        "# Run Health Summary",
        "",
        f"Run ID: {telemetry.get('run_id')}",
        "",
        "## Gate Results",
    ]
    for gate, result in gate_results.items():
        summary_lines.append(f"- {gate}: {result}")
    summary_lines.extend(["", "## Determinism Status"])
    for phase, status in determinism_status.items():
        summary_lines.append(f"- {phase}: {status}")
    summary_lines.extend(["", "## Failure Counts"])
    for failure_type, count in failure_counts.items():
        summary_lines.append(f"- {failure_type}: {count}")

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print(f"Wrote run health summary: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
