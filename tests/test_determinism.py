from __future__ import annotations

from generator.determinism import bijectivity_check, replay_determinism_check


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
    assert failure is None
    assert report.match is True


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
    assert failure is not None
    assert failure.Type == "deterministic_failure"
    assert report.match is False


def test_bijectivity_check_detects_collision() -> None:
    failure = bijectivity_check(["id-1", "id-1"])
    assert failure is not None
    assert failure.Type == "deterministic_failure"
