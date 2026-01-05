#!/usr/bin/env python3
"""Validate invariant registry coverage and enforcement."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_cores.cli_arg_parser_core import build_parser, parse_args
from generator.failure_emitter import FailureEmitter, FailureLabel
from generator.invariant_registry import (
    build_coverage_report,
    load_invariants_yaml,
    load_registry,
    validate_registry,
)


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Validate invariant coverage.")
    parser.add_argument(
        "--invariants-path",
        type=Path,
        # GOVERNANCE SOURCE REMOVED
        # Canonical governance will be resolved from directive_core/docs/
        default=None,
        help="Path to invariants file.",
    )
    parser.add_argument(
        "--registry-path",
        type=Path,
        # GOVERNANCE SOURCE REMOVED
        # Canonical governance will be resolved from directive_core/docs/
        default=None,
        help="Path to the invariants registry JSON file.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=Path("artifacts/evidence_pack/invariant_coverage_report.json"),
        help="Path to write coverage report.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="local-run",
        help="Run identifier for emitted failure labels.",
    )
    return parse_args(parser)


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/failures"))

    if args.invariants_path is None or args.registry_path is None:
        emitter.emit(
            FailureLabel(
                Type="io_failure",
                message="Governance source removed: invariants paths must be supplied explicitly",
                phase_id="validate",
                evidence={
                    "invariants_path": str(args.invariants_path),
                    "registry_path": str(args.registry_path),
                },
            ),
            run_id=args.run_id,
        )
        return 1

    if not args.invariants_path.exists():
        emitter.emit(
            FailureLabel(
                Type="io_failure",
                message="Invariant declarations missing",
                phase_id="validate",
                evidence={"path": str(args.invariants_path)},
            ),
            run_id=args.run_id,
        )
        return 1

    if not args.registry_path.exists():
        emitter.emit(
            FailureLabel(
                Type="io_failure",
                message="Invariant registry missing",
                phase_id="validate",
                evidence={"path": str(args.registry_path)},
            ),
            run_id=args.run_id,
        )
        return 1

    declared_invariants = load_invariants_yaml(args.invariants_path)
    registry_payload = load_registry(args.registry_path)
    registry_errors = validate_registry(registry_payload)
    if registry_errors:
        emitter.emit(
            FailureLabel(
                Type="schema_failure",
                message="Invariant registry validation failed",
                phase_id="validate",
                evidence={"errors": registry_errors},
            ),
            run_id=args.run_id,
        )
        return 1

    report = build_coverage_report(
        declared_invariants=declared_invariants,
        registry_payload=registry_payload,
        repo_root=Path("."),
    )
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if report.get("status") != "pass":
        missing_ids = [
            entry.get("id") for entry in report.get("missing_enforcement", [])
        ]
        emitter.emit(
            FailureLabel(
                Type="schema_failure",
                message="Invariant enforcement coverage failed",
                phase_id="validate",
                evidence={
                    "missing_registry": report.get("missing_registry", []),
                    "missing_enforcement": report.get("missing_enforcement", []),
                    "invariant_ids": [item for item in missing_ids if item],
                },
            ),
            run_id=args.run_id,
        )
        return 1

    print("Invariant coverage validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
