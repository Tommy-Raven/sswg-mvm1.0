"""
cli_spec_validator.py — CLI spec validation for sswg mvm.

Validation output is a non_operational_output decision_trace.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import yaml

CANONICAL_ORDER = [
    "ingest",
    "normalize",
    "parse",
    "analyze",
    "generate",
    "validate",
    "compare",
    "interpret",
    "log",
]
DETERMINISTIC_PHASES = {"normalize", "analyze", "validate", "compare"}
ALLOWED_COMPARE_METRICS = {"iou", "jaccard"}

SCHEMA: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "output_mode": "non_operational_output",
    "type": "object",
    "required": ["anchor", "cli", "phase_model", "terminology"],
}


def _load_spec(path: Path) -> Dict[str, Any]:
    payload = path.read_text(encoding="utf-8")
    data = yaml.safe_load(payload)
    if not isinstance(data, dict):
        raise ValueError("cli_spec.yaml must parse to a mapping")
    return data


def _issue(category: str, message: str, path: str) -> Dict[str, str]:
    return {"category": category, "message": message, "path": path}


def _validate_anchor(data: Dict[str, Any], issues: List[Dict[str, str]]) -> None:
    anchor = data.get("anchor")
    if not isinstance(anchor, dict):
        issues.append(_issue("invariant", "anchor block is required", "anchor"))
        return
    for key in ("anchor_id", "anchor_version", "scope", "owner", "status"):
        if key not in anchor:
            issues.append(_issue("invariant", f"anchor.{key} is required", f"anchor.{key}"))


def _validate_terminology(data: Dict[str, Any], issues: List[Dict[str, str]]) -> None:
    terminology = data.get("terminology")
    if not isinstance(terminology, dict):
        issues.append(
            _issue("constraint", "terminology block is required", "terminology")
        )
        return
    if terminology.get("terminology_compliance") != "TERMINOLOGY.md@1.0.0":
        issues.append(
            _issue(
                "constraint",
                "terminology_compliance must reference TERMINOLOGY.md@1.0.0",
                "terminology.terminology_compliance",
            )
        )
    if terminology.get("output_mode") != "non_operational_output":
        issues.append(
            _issue(
                "constraint",
                "output_mode must be non_operational_output",
                "terminology.output_mode",
            )
        )


def _validate_phase_model(data: Dict[str, Any], issues: List[Dict[str, str]]) -> None:
    phase_model = data.get("phase_model")
    if not isinstance(phase_model, dict):
        issues.append(_issue("invariant", "phase_model block is required", "phase_model"))
        return
    if phase_model.get("canonical_order") != CANONICAL_ORDER:
        issues.append(
            _issue(
                "invariant",
                "canonical_order must match full_9_phase",
                "phase_model.canonical_order",
            )
        )
    phases = phase_model.get("phases")
    if not isinstance(phases, list):
        issues.append(_issue("invariant", "phases list is required", "phase_model.phases"))
        return
    phase_names = [phase.get("name") for phase in phases if isinstance(phase, dict)]
    if phase_names != CANONICAL_ORDER:
        issues.append(
            _issue(
                "invariant",
                "phases list must match full_9_phase order",
                "phase_model.phases",
            )
        )
    for phase in phases:
        if not isinstance(phase, dict):
            continue
        name = phase.get("name")
        deterministic_required = phase.get("deterministic_required")
        if name in DETERMINISTIC_PHASES and deterministic_required is not True:
            issues.append(
                _issue(
                    "constraint",
                    "deterministic_required must be true for deterministic phases",
                    f"phase_model.phases[{name}].deterministic_required",
                )
            )
        if name == "interpret" and deterministic_required is True:
            issues.append(
                _issue(
                    "constraint",
                    "interpret must be labeled nondeterministic",
                    "phase_model.phases[interpret].deterministic_required",
                )
            )
        if name == "compare":
            constraints = phase.get("constraints", {})
            metrics = constraints.get("overlap_metrics_allowed")
            if metrics is not None:
                invalid = [metric for metric in metrics if metric not in ALLOWED_COMPARE_METRICS]
                if invalid:
                    issues.append(
                        _issue(
                            "constraint",
                            "compare overlap_metrics_allowed must be iou or jaccard",
                            "phase_model.phases[compare].constraints.overlap_metrics_allowed",
                        )
                    )


def validate_spec(path: Path) -> Dict[str, Any]:
    data = _load_spec(path)
    issues: List[Dict[str, str]] = []
    _validate_anchor(data, issues)
    _validate_terminology(data, issues)
    _validate_phase_model(data, issues)
    result = "pass" if not issues else "fail"
    redteam_report = [
        {
            "category": issue["category"],
            "message": issue["message"],
            "path": issue["path"],
        }
        for issue in issues
    ]
    return {
        "metadata": {
            "artifact_type": "decision_trace",
            "terminology_compliance": "TERMINOLOGY.md@1.0.0",
            "output_mode": "non_operational_output",
        },
        "result": result,
        "redteam_report": redteam_report,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI spec validation output (non_operational_output).",
    )
    parser.add_argument(
        "spec_path",
        type=Path,
        help="Path reference to cli_spec.yaml.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Displays JSON validation output.",
    )
    return parser.parse_args()


def _main() -> int:
    args = _parse_args()
    result = validate_spec(args.spec_path)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))
    if result["result"] == "pass":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(_main())
