---
anchor:
  anchor_id: docs_compliance_compliance_checklist
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# Promotion Readiness Checklist

| Gate | Command | Artifact | Pass criteria |
| --- | --- | --- | --- |
| PDL schema validation | `python3 -m generator.pdl_validator pdl/example_full_9_phase.yaml schemas --report-dir artifacts/validation --run-id <run_id>` | `artifacts/validation/pdl_validation_<hash>.json` | `result: pass` |
| Phase schema validation | `python3 scripts/validate_pdl_artifacts.py --pdl-dir pdl --schema-dir schemas --report-dir artifacts/validation --run-id <run_id>` | `artifacts/validation/pdl_validation_<hash>.json` | All PDL validations pass |
| Phase IO manifest + collapse detection | `python3 scripts/generate_phase_io_manifest.py pdl/example_full_9_phase.yaml --observed tests/fixtures/observed_io.json --output artifacts/phase_io/phase_io_manifest.json --run-id <run_id>` | `artifacts/phase_io/phase_io_manifest.json` | No phase collapse failure |
| Determinism replay | `python3 scripts/run_determinism_replay.py --phase-outputs tests/fixtures/phase_outputs.json --output artifacts/determinism/determinism_report.json --run-id <run_id>` | `artifacts/determinism/determinism_report.json` | `match: true` |
| Failure labeling tests | `pytest tests/test_failure_emitter.py` | `artifacts/failures/failure_<hash>.json` (on fail) | All tests pass |
| Anchor enforcement | `python3 scripts/validate_anchors.py artifacts/validation/pdl_validation_<hash>.json --registry config/anchor_registry.json --run-id <run_id>` | `config/anchor_registry.json` | Anchor registered or canonical lock enforced |
| Overlay validation | `python3 scripts/validate_overlay.py tests/fixtures/overlay_descriptor.json` | `artifacts/failures/failure_<hash>.json` (on fail) | Overlay descriptor passes |
| Promotion readiness gate | `python3 scripts/run_promotion_readiness.py --run-id <run_id>` | `artifacts/evidence_pack/<run_id>/` | All gates pass, evidence pack present |
