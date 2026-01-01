from __future__ import annotations

import json
from pathlib import Path

from pdl.default_pdl import load_default_phases


def _phase_name_from_schema(schema_path: Path) -> str:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    phase_def = schema["$defs"]["phase"]
    for entry in phase_def.get("allOf", []):
        properties = entry.get("properties")
        if properties and "name" in properties:
            return properties["name"]["const"]
    raise AssertionError(f"No phase name const found in {schema_path}")


def test_default_phases_match_phase_set_schema() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    schema_dir = repo_root / "schemas"
    phase_set_schema = json.loads(
        (schema_dir / "pdl-phase-set.json").read_text(encoding="utf-8")
    )
    prefix_items = phase_set_schema["properties"]["phases"]["prefixItems"]
    expected_phase_names = []
    for item in prefix_items:
        ref_path = item["$ref"].split("#")[0]
        expected_phase_names.append(
            _phase_name_from_schema(schema_dir / ref_path)
        )

    default_phase_names = list(load_default_phases().keys())

    assert default_phase_names == expected_phase_names
