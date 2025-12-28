from __future__ import annotations

from pathlib import Path

from generator.phase_io import build_phase_io_manifest, detect_phase_collapse, load_pdl
from tests.assertions import require


def test_phase_io_manifest_pass() -> None:
    pdl_obj = load_pdl(Path("pdl/example_full_9_phase.yaml"))
    observed = {"parse": {"inputs": ["normalized_payload"], "outputs": ["parsed_payload"]}}
    manifest = build_phase_io_manifest(pdl_obj, observed)
    failure = detect_phase_collapse(manifest, pdl_obj)
    require(failure is None, "Expected no failure for valid manifest")


def test_phase_io_manifest_detects_generation() -> None:
    pdl_obj = load_pdl(Path("pdl/example_full_9_phase.yaml"))
    observed = {"parse": {"inputs": ["normalized_payload"], "outputs": ["parsed_payload"], "actions": ["generate"]}}
    manifest = build_phase_io_manifest(pdl_obj, observed)
    failure = detect_phase_collapse(manifest, pdl_obj)
    require(failure is not None, "Expected phase collapse failure")
    require(failure.Type == "schema_failure", "Expected schema_failure label")
    require(failure.phase_id == "parse", "Expected parse phase_id")
