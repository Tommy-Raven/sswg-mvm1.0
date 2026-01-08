"""Failure label creation and persistence helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from generator.hashing import hash_data
from generator.sanitizer import sanitize_payload

ALLOWED_FAILURE_TYPES = {
    "deprecation_violation",
    "deterministic_failure",
    "constitution_precedence_violation",
    "governance_anchor_violation",
    "governance_freeze_violation",
    "governance_ingestion_order_violation",
    "governance_source_violation",
    "governance_violation",
    "schema_failure",
    "missing_governance_document",
    "tooling_reference_violation",
    "io_failure",
    "tool_mismatch",
    "reproducibility_failure",
}


@dataclass(frozen=True)
class FailureLabel:  # pylint: disable=invalid-name
    """Structured failure label payload."""

    Type: str
    message: str
    phase_id: str
    path: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        """Return the label as a serializable dictionary."""
        payload: Dict[str, Any] = {
            "Type": self.Type,
            "message": self.message,
            "phase_id": self.phase_id,
            "path": self.path,
        }
        if self.path is not None:
            payload["path"] = self.path
        if self.evidence is not None:
            payload["evidence"] = self.evidence
        return payload


def validate_failure_label(label: FailureLabel) -> None:
    """Validate the failure label contents against allowed types."""
    if label.Type not in ALLOWED_FAILURE_TYPES:
        raise ValueError(f"Unknown failure Type: {label.Type}")
    if not label.message:
        raise ValueError("Failure label message must be non-empty")
    if not label.phase_id:
        raise ValueError("Failure label phase_id must be non-empty")
    if label.path is not None and not label.path:
        raise ValueError("Failure label path must be non-empty when provided")


class FailureEmitter:  # pylint: disable=too-few-public-methods
    """Emit failure label payloads to disk."""

    def __init__(self, output_dir: Path) -> None:
        """Initialize the emitter output directory."""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def emit(
        self,
        label: FailureLabel,
        *,
        run_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Write a failure label payload to disk and return its path."""
        validate_failure_label(label)
        sanitized_label = FailureLabel(
            Type=label.Type,
            message=label.message,
            phase_id=label.phase_id,
            path=label.path,
            evidence=sanitize_payload(label.evidence) if label.evidence else None,
        )
        payload: Dict[str, Any] = {
            "run_id": run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "label": sanitized_label.as_dict(),
        }
        if context is not None:
            payload["context"] = sanitize_payload(context)
        payload["inputs_hash"] = hash_data(payload["label"])
        filename = f"failure_{payload['inputs_hash']}.json"
        path = self.output_dir / filename
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path
