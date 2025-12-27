from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from generator.hashing import hash_data
from generator.sanitizer import sanitize_payload

ALLOWED_FAILURE_TYPES = {
    "deterministic_failure",
    "schema_failure",
    "io_failure",
    "tool_mismatch",
    "reproducibility_failure",
}


@dataclass(frozen=True)
class FailureLabel:
    Type: str
    message: str
    phase_id: str
    evidence: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "Type": self.Type,
            "message": self.message,
            "phase_id": self.phase_id,
        }
        if self.evidence is not None:
            payload["evidence"] = self.evidence
        return payload


def validate_failure_label(label: FailureLabel) -> None:
    if label.Type not in ALLOWED_FAILURE_TYPES:
        raise ValueError(f"Unknown failure Type: {label.Type}")
    if not label.message:
        raise ValueError("Failure label message must be non-empty")
    if not label.phase_id:
        raise ValueError("Failure label phase_id must be non-empty")


class FailureEmitter:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def emit(
        self,
        label: FailureLabel,
        *,
        run_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Path:
        validate_failure_label(label)
        sanitized_label = FailureLabel(
            Type=label.Type,
            message=label.message,
            phase_id=label.phase_id,
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
