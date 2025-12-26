#!/usr/bin/env python3
"""
Error taxonomy, severity routing, and incident recording helpers for MVM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from ai_monitoring.structured_logger import log_event


class ErrorClass(str, Enum):
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    BEHAVIORAL = "behavioral"
    SAFETY = "safety"
    OPERATIONAL = "operational"


class Severity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "informational"


@dataclass
class ErrorSignal:
    message: str
    error_class: ErrorClass
    severity: Severity
    source: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IncidentRecord:
    workflow_id: str
    message: str
    error_class: ErrorClass
    severity: Severity
    source: str
    context: Dict[str, Any] = field(default_factory=dict)
    remediation: Optional[str] = None
    decision: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "message": self.message,
            "error_class": self.error_class.value,
            "severity": self.severity.value,
            "source": self.source,
            "context": self.context,
            "remediation": self.remediation,
            "decision": self.decision,
            "created_at": self.created_at,
        }


def classify_exception(exc: Exception, *, source: str) -> ErrorSignal:
    return ErrorSignal(
        message=str(exc),
        error_class=ErrorClass.OPERATIONAL,
        severity=Severity.MAJOR,
        source=source,
        context={"exception_type": type(exc).__name__},
    )


def classify_validation_failure(error_count: int) -> ErrorSignal:
    return ErrorSignal(
        message=f"Schema validation failed ({error_count} issue(s)).",
        error_class=ErrorClass.STRUCTURAL,
        severity=Severity.CRITICAL,
        source="schema_validation",
        context={"error_count": error_count},
    )


def recovery_decision(error_class: ErrorClass, severity: Severity) -> Dict[str, Any]:
    decision: Dict[str, Any] = {"action": "monitor", "quarantine": False}

    if severity == Severity.CRITICAL:
        decision.update(
            {"action": "rollback", "quarantine": True, "escalate": True}
        )
    elif severity == Severity.MAJOR:
        decision.update({"action": "targeted_fix", "quarantine": True})
    elif severity == Severity.MINOR:
        decision.update({"action": "defer_fix"})

    if error_class == ErrorClass.SAFETY:
        decision.update({"action": "quarantine", "quarantine": True, "escalate": True})

    return decision


def build_incident(
    workflow_id: str, signal: ErrorSignal, *, remediation: Optional[str] = None
) -> IncidentRecord:
    decision = recovery_decision(signal.error_class, signal.severity)
    record = IncidentRecord(
        workflow_id=workflow_id,
        message=signal.message,
        error_class=signal.error_class,
        severity=signal.severity,
        source=signal.source,
        context=signal.context,
        remediation=remediation,
        decision=decision.get("action"),
    )
    log_event(
        "mvm.incident.recorded",
        {
            "workflow_id": workflow_id,
            "error_class": signal.error_class.value,
            "severity": signal.severity.value,
            "source": signal.source,
            "decision": decision.get("action"),
            "quarantine": decision.get("quarantine", False),
        },
    )
    return record


def apply_incident(
    workflow: Dict[str, Any], incident: IncidentRecord, decision: Dict[str, Any]
) -> Dict[str, Any]:
    metadata = workflow.setdefault("metadata", {})
    apply_incident_metadata(metadata, incident, decision)
    return workflow


def apply_incident_metadata(
    metadata: Dict[str, Any], incident: IncidentRecord, decision: Dict[str, Any]
) -> Dict[str, Any]:
    incident_log = metadata.setdefault("incident_log", [])
    incident_log.append(incident.to_dict())

    if decision.get("quarantine"):
        metadata["quarantine"] = True
        metadata.setdefault("quarantine_reason", incident.message)

    metadata.setdefault("recovery_decisions", []).append(decision)
    return metadata
