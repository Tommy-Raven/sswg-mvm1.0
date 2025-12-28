from __future__ import annotations

import json
from pathlib import Path

import pytest

from generator.pdl_validator import PDLValidationError, validate_pdl_file_with_report
from tests.assertions import require


def test_pdl_validation_report_pass(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports"
    validate_pdl_file_with_report(
        pdl_path=Path("pdl/example_full_9_phase.yaml"),
        schema_dir=Path("schemas"),
        report_dir=report_dir,
        run_id="test-run",
    )
    reports = list(report_dir.glob("pdl_validation_*.json"))
    require(reports, "Expected validation report to be written")
    payload = json.loads(reports[0].read_text(encoding="utf-8"))
    require(payload["result"] == "pass", "Expected pass result")


def test_pdl_validation_report_fail(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports"
    with pytest.raises(PDLValidationError):
        validate_pdl_file_with_report(
            pdl_path=Path("tests/fixtures/pdl/invalid_full_9_phase.yaml"),
            schema_dir=Path("schemas"),
            report_dir=report_dir,
            run_id="test-run",
    )
    reports = list(report_dir.glob("pdl_validation_*.json"))
    require(reports, "Expected validation report to be written")
    payload = json.loads(reports[0].read_text(encoding="utf-8"))
    require(payload["result"] == "fail", "Expected fail result")
    failure_logs = list((report_dir / "failures").glob("failure_*.json"))
    require(failure_logs, "Expected failure logs to be written")
    failure_payload = json.loads(failure_logs[0].read_text(encoding="utf-8"))
    require(
        failure_payload["label"]["Type"] == "schema_failure",
        "Expected schema_failure label",
    )
    require(
        failure_payload["label"]["phase_id"] == "validate",
        "Expected validate phase_id",
    )
