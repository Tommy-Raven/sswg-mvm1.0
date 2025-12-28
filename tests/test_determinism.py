from __future__ import annotations

from generator.determinism import bijectivity_check, replay_determinism_check
from tests.assertions import require


def test_determinism_replay_pass() -> None:
    phase_outputs = {
        "normalize": {"payload": "normalized"},
        "analyze": {"metrics": {"id": "metric-1", "value": 1}},
        "validate": {"status": "ok"},
        "compare": {"diff": "none"},
    }
    failure, report = replay_determinism_check(
        run_id="run-1",
        phase_outputs=phase_outputs,
        required_phases=["normalize", "analyze", "validate", "compare"],
    )
    require(failure is None, "Expected determinism replay to pass")
    require(report.match is True, "Expected determinism report to match")


def test_determinism_replay_failure() -> None:
    phase_outputs = {
        "normalize": {"payload": "normalized"},
        "analyze": {"metrics": {"id": "metric-1", "value": 1}},
        "validate": {"status": "ok"},
        "compare": {"diff": "none"},
    }
    failure, report = replay_determinism_check(
        run_id="run-1",
        phase_outputs=phase_outputs,
        required_phases=["normalize", "analyze", "validate", "compare"],
        inject_phase="compare",
    )
    require(failure is not None, "Expected determinism replay failure")
    require(
        failure.Type == "deterministic_failure",
        "Expected deterministic_failure label",
    )
    require(report.match is False, "Expected determinism report to mismatch")


def test_bijectivity_check_detects_collision() -> None:
    failure = bijectivity_check(["id-1", "id-1"])
    require(failure is not None, "Expected bijectivity failure")
    require(
        failure.Type == "deterministic_failure",
        "Expected deterministic_failure label",
    )
