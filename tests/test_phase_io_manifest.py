from __future__ import annotations

from pathlib import Path

from generator.phase_io import build_phase_io_manifest, detect_phase_collapse, load_pdl


def test_phase_io_manifest_pass() -> None:
    pdl_obj = load_pdl(Path("pdl/example_full_9_phase.yaml"))
    observed = {"parse": {"inputs": ["normalized_payload"], "outputs": ["parsed_payload"]}}
    manifest = build_phase_io_manifest(pdl_obj, observed)
    failure = detect_phase_collapse(manifest, pdl_obj)
    assert failure is None


def test_phase_io_manifest_detects_generation() -> None:
    pdl_obj = load_pdl(Path("pdl/example_full_9_phase.yaml"))
    observed = {"parse": {"inputs": ["normalized_payload"], "outputs": ["parsed_payload"], "actions": ["generate"]}}
    manifest = build_phase_io_manifest(pdl_obj, observed)
    failure = detect_phase_collapse(manifest, pdl_obj)
    assert failure is not None
    assert failure.Type == "schema_failure"
    assert failure.phase_id == "parse"
