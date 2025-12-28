from __future__ import annotations

import json
from pathlib import Path

import pytest

from generator.failure_emitter import (
    FailureEmitter,
    FailureLabel,
    validate_failure_label,
)
from tests.assertions import require


def test_failure_label_validation_rejects_unknown_type() -> None:
    with pytest.raises(ValueError):
        validate_failure_label(
            FailureLabel(
                Type="unknown",
                message="bad type",
                phase_id="validate",
            )
        )


def test_failure_label_validation_rejects_missing_phase() -> None:
    with pytest.raises(ValueError):
        validate_failure_label(
            FailureLabel(
                Type="schema_failure",
                message="missing phase",
                phase_id="",
            )
        )


def test_failure_emitter_redacts_secrets(tmp_path: Path) -> None:
    emitter = FailureEmitter(tmp_path)
    label = FailureLabel(
        Type="schema_failure",
        message="failure with secret evidence",
        phase_id="validate",
        evidence={"token": "secret", "nested": {"password": "value"}},
    )
    path = emitter.emit(label, run_id="run-1")
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(
        payload["label"]["evidence"]["token"] == "[REDACTED]",
        "Expected token to be redacted",
    )
    require(
        payload["label"]["evidence"]["nested"]["password"] == "[REDACTED]",
        "Expected password to be redacted",
    )
