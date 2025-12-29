#!/usr/bin/env python3
"""
ai_monitoring/health_card.py — Per-run health card artifact + renderer.

The health card summarizes:
- gate pass/fail
- determinism status
- overlay chain + compatibility
- evaluation deltas
- provenance integrity
- security scan result
- audit certificate presence
- promotion status
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .structured_logger import log_event


DETERMINISTIC_PHASES = ("normalize", "analyze", "validate", "compare")


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _first_existing(paths: Iterable[Path]) -> Optional[Path]:
    for path in paths:
        if path.exists():
            return path
    return None


def _normalize_status(value: Optional[str]) -> str:
    if value in {"pass", "fail", "unknown"}:
        return value
    return "unknown"


def _extract_gate_results(
    *,
    log_report: Optional[Dict[str, Any]],
    validation_passed: bool,
) -> Dict[str, str]:
    gate_defaults = {
        "schema_validation": "unknown",
        "phase_schema_validation": "unknown",
        "invariants_validation": "unknown",
        "reproducibility_validation": "unknown",
    }
    if log_report:
        phase_status = log_report.get("phase_status", {})
        for key in gate_defaults:
            if key in phase_status:
                gate_defaults[key] = _normalize_status(phase_status.get(key))
    elif validation_passed:
        gate_defaults["schema_validation"] = "pass"
    return gate_defaults


def _extract_determinism(
    *,
    determinism_report: Optional[Dict[str, Any]],
    phase_status: Dict[str, Dict[str, object]],
) -> Dict[str, Any]:
    if determinism_report:
        match = bool(determinism_report.get("match", False))
        return {
            "status": "pass" if match else "fail",
            "match": match,
            "report_path": determinism_report.get("_source_path"),
            "diff_summary": determinism_report.get("diff_summary", {}),
        }

    status_by_phase: Dict[str, str] = {}
    for phase in DETERMINISTIC_PHASES:
        entry = phase_status.get(phase, {})
        status = "unknown"
        if entry.get("status") == "success":
            status = "pass"
        elif entry.get("status") == "failed":
            status = "fail"
        status_by_phase[phase] = status

    overall = "unknown"
    if all(value == "pass" for value in status_by_phase.values()):
        overall = "pass"
    elif any(value == "fail" for value in status_by_phase.values()):
        overall = "fail"

    return {"status": overall, "by_phase": status_by_phase}


def _extract_overlay_chain(
    *,
    overlay_manifest: Optional[Dict[str, Any]],
    overlay_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    overlays = []
    if overlay_manifest:
        overlays = overlay_manifest.get("overlays", [])
        if overlays and isinstance(overlays[0], dict) and "overlay_id" not in overlays[0]:
            overlays = overlay_manifest.get("overlay_chain", [])
    compatibility_summary = {
        "status": "unknown",
        "overlays": [],
    }
    if overlay_report:
        reports = overlay_report.get("overlays", [])
        compatibility_summary["overlays"] = reports
        if reports:
            if all(item.get("lint_pass") and item.get("ambiguity_pass") for item in reports):
                compatibility_summary["status"] = "pass"
            else:
                compatibility_summary["status"] = "fail"

    return {
        "overlays": overlays,
        "compatibility": compatibility_summary,
    }


def _extract_eval_deltas(eval_report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not eval_report:
        return {"status": "unknown"}
    passed = bool(eval_report.get("passed", False))
    return {
        "status": "pass" if passed else "fail",
        "passed": passed,
        "deltas": eval_report.get("deltas", {}),
        "regressions": eval_report.get("regressions", {}),
        "report_path": eval_report.get("_source_path"),
    }


def _extract_provenance_integrity(
    provenance_manifest: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    if not provenance_manifest:
        return {"status": "unknown"}
    required = {"run_id", "inputs_hash", "overlay_chain", "artifacts"}
    present = required.issubset(provenance_manifest.keys())
    return {
        "status": "pass" if present else "fail",
        "manifest_path": provenance_manifest.get("_source_path"),
    }


def _extract_security_scan(report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not report:
        return {"status": "unknown"}
    status = report.get("status") or report.get("result")
    return {
        "status": _normalize_status(str(status).lower() if status else None),
        "report_path": report.get("_source_path"),
    }


def _extract_audit_certificate(path: Optional[Path]) -> Dict[str, Any]:
    if not path:
        return {"present": False}
    return {"present": path.exists(), "path": str(path)}


def _extract_promotion_status(report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not report:
        return {"status": "unknown"}
    decision = report.get("promotion_decision")
    status = "unknown"
    if decision == "approve":
        status = "approved"
    elif decision == "reject":
        status = "rejected"
    return {
        "status": status,
        "decision": decision,
        "report_path": report.get("_source_path"),
    }


def _attach_source_path(payload: Optional[Dict[str, Any]], path: Optional[Path]) -> Optional[Dict[str, Any]]:
    if payload is None:
        return None
    if path:
        payload = dict(payload)
        payload["_source_path"] = str(path)
    return payload


def build_health_card(
    *,
    workflow: Dict[str, Any],
    phase_status: Dict[str, Dict[str, object]],
    validation_passed: bool,
    run_id: Optional[str] = None,
    evidence_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    run_id = run_id or workflow.get("workflow_id") or workflow.get("id") or "unknown_run"
    evidence_dir = evidence_dir or Path("artifacts") / "evidence_pack" / run_id

    log_report_path = evidence_dir / "log_phase_report.json"
    determinism_path = evidence_dir / "determinism_report.json"
    overlay_manifest_path = evidence_dir / "overlay_chain_manifest.json"
    overlay_report_path = evidence_dir / "overlay_promotion_report.json"
    eval_report_path = evidence_dir / "eval_report.json"
    provenance_path = evidence_dir / "provenance_manifest.json"

    log_report = _attach_source_path(_load_json(log_report_path), log_report_path)
    determinism_report = _attach_source_path(_load_json(determinism_path), determinism_path)
    overlay_manifest = _attach_source_path(_load_json(overlay_manifest_path), overlay_manifest_path)
    overlay_report = _attach_source_path(_load_json(overlay_report_path), overlay_report_path)
    eval_report = _attach_source_path(_load_json(eval_report_path), eval_report_path)
    provenance_manifest = _attach_source_path(_load_json(provenance_path), provenance_path)

    security_report_path = _first_existing(
        [
            evidence_dir / "security_scan.json",
            Path("artifacts") / "security" / "security_scan.json",
            Path("artifacts") / "security_scan.json",
        ]
    )
    security_report = _attach_source_path(
        _load_json(security_report_path) if security_report_path else None,
        security_report_path,
    )

    audit_certificate_path = _first_existing(
        [
            Path("artifacts") / "audit" / "audit_certificate.json",
            evidence_dir / "audit_certificate.json",
        ]
    )

    promotion_checklist_path = _first_existing(
        [
            Path("artifacts") / "governance" / "promotion_checklist.json",
            evidence_dir / "promotion_checklist.json",
        ]
    )
    promotion_checklist = _attach_source_path(
        _load_json(promotion_checklist_path) if promotion_checklist_path else None,
        promotion_checklist_path,
    )

    card = {
        "anchor": {
            "anchor_id": "health_card",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "ai_monitoring.health_card",
            "status": "draft",
        },
        "run_id": run_id,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "gates": _extract_gate_results(
            log_report=log_report,
            validation_passed=validation_passed,
        ),
        "determinism": _extract_determinism(
            determinism_report=determinism_report,
            phase_status=phase_status,
        ),
        "overlay_chain": _extract_overlay_chain(
            overlay_manifest=overlay_manifest,
            overlay_report=overlay_report,
        ),
        "eval_deltas": _extract_eval_deltas(eval_report),
        "provenance_integrity": _extract_provenance_integrity(provenance_manifest),
        "security_scan": _extract_security_scan(security_report),
        "audit_certificate": _extract_audit_certificate(audit_certificate_path),
        "promotion_status": _extract_promotion_status(promotion_checklist),
        "phase_status": phase_status,
    }
    return card


def write_health_card(card: Dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(card, indent=2), encoding="utf-8")
    log_event("health_card.written", {"path": str(output_path), "run_id": card.get("run_id")})
    return output_path


def render_health_card(card: Dict[str, Any]) -> None:
    print("----- RUN HEALTH CARD -----")
    print(f"Run ID: {card.get('run_id')}")
    print(f"Generated: {card.get('generated_at')}")
    print("\nGates:")
    for gate, status in card.get("gates", {}).items():
        print(f"  - {gate}: {status}")
    determinism = card.get("determinism", {})
    print(f"\nDeterminism: {determinism.get('status', 'unknown')}")
    if "by_phase" in determinism:
        for phase, status in determinism.get("by_phase", {}).items():
            print(f"  - {phase}: {status}")
    overlay_chain = card.get("overlay_chain", {})
    overlays = overlay_chain.get("overlays", [])
    print(f"\nOverlays: {len(overlays)}")
    compat = overlay_chain.get("compatibility", {})
    print(f"Overlay Compatibility: {compat.get('status', 'unknown')}")
    eval_deltas = card.get("eval_deltas", {})
    print(f"\nEval Deltas: {eval_deltas.get('status', 'unknown')}")
    print(f"Provenance Integrity: {card.get('provenance_integrity', {}).get('status', 'unknown')}")
    print(f"Security Scan: {card.get('security_scan', {}).get('status', 'unknown')}")
    audit = card.get("audit_certificate", {})
    print(f"Audit Certificate Present: {audit.get('present', False)}")
    promo = card.get("promotion_status", {})
    print(f"Promotion Status: {promo.get('status', 'unknown')}")
    print("---------------------------")
    log_event("health_card.rendered", {"run_id": card.get("run_id")})


__all__ = [
    "build_health_card",
    "render_health_card",
    "write_health_card",
]
