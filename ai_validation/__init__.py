#!/usr/bin/env python3
"""
ai_validation package — Validation utilities for SSWG MVM.

Public surface (MVM level):

- validate_workflow(workflow_obj, schema_name="workflow_schema.json")
- validate_json(obj, schema_name=None)

Higher-level modules can import from here instead of directly from
schema_validator if they want a stable, unified interface.
"""

from __future__ import annotations

from .error_protocol import (
    ErrorClass,
    ErrorSignal,
    IncidentRecord,
    Severity,
    apply_incident,
    apply_incident_metadata,
    build_incident,
    classify_exception,
    classify_validation_failure,
    recovery_decision,
)
from .schema_validator import validate_workflow, validate_json

__all__ = [
    "ErrorClass",
    "ErrorSignal",
    "IncidentRecord",
    "Severity",
    "apply_incident",
    "apply_incident_metadata",
    "build_incident",
    "classify_exception",
    "classify_validation_failure",
    "recovery_decision",
    "validate_workflow",
    "validate_json",
]


def get_version() -> str:
    """
    Return a simple version identifier for the validation subsystem.

    This is mostly a convenience hook for telemetry or debug output.
    """
    # You can bump this manually when you evolve validation behavior.
    return "ai_validation-mvm-0.1.0"
