"""Tests for shared CLI spec validator core entrypoints."""

import json
import sys
from pathlib import Path
from subprocess import run as subprocess_run

from cli.cli_spec_validator_core import validate_spec
from tests.assertions import require


def _write_spec(tmp_path: Path) -> Path:
    path = tmp_path / "cli_spec.yaml"
    path.write_text(
        """
anchor:
  anchor_id: cli_spec
  anchor_version: "1.2.0+mvm"
  scope: config
  owner: sswg-core
  status: draft

terminology:
  terminology_compliance: "TERMINOLOGY.md@1.0.0"
  output_mode: non_operational_output

cli:
  name: sswg
  reference: docs/ARGS.md
  commands: []

phase_model:
  pipeline_profile: full_9_phase
  canonical_order:
    - ingest
    - normalize
    - parse
    - analyze
    - generate
    - validate
    - compare
    - interpret
    - log
  phases:
    - name: ingest
      deterministic_required: false
    - name: normalize
      deterministic_required: true
    - name: parse
      deterministic_required: false
    - name: analyze
      deterministic_required: true
    - name: generate
      deterministic_required: false
    - name: validate
      deterministic_required: true
    - name: compare
      deterministic_required: true
      constraints:
        overlap_metrics_allowed:
          - iou
    - name: interpret
      deterministic_required: false
    - name: log
      deterministic_required: false
""".lstrip(),
        encoding="utf-8",
    )
    return path


def _run_entrypoint(entry_path: str, spec_path: Path) -> dict:
    result = subprocess_run(  # nosec B603
        [sys.executable, entry_path, str(spec_path), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    require(result.returncode == 0, f"Expected {entry_path} to succeed")
    return json.loads(result.stdout)


def test_validate_spec_and_entrypoints(tmp_path: Path) -> None:
    spec_path = _write_spec(tmp_path)

    core_result = validate_spec(spec_path)
    require(core_result["result"] == "pass", "Expected core validation to pass")

    top_level_result = _run_entrypoint("cli_spec_validator.py", spec_path)
    package_result = _run_entrypoint("cli/cli_spec_validator.py", spec_path)

    require(
        top_level_result["result"] == "pass",
        "Expected top-level entrypoint validation to pass",
    )
    require(
        package_result["result"] == "pass",
        "Expected cli package entrypoint validation to pass",
    )
    require(
        top_level_result == package_result == core_result,
        "Expected entrypoints to match core validation output",
    )
