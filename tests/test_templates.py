"""Schema validation tests for bundled templates."""

import json
from pathlib import Path

from ai_validation.schema_validator import validate_template
from tests.assertions import require


def test_meta_reflection_template_valid():
    path = Path("data/templates/meta_reflection_template.json")
    obj = json.loads(path.read_text(encoding="utf-8"))
    ok, errors = validate_template(obj)
    require(
        ok,
        f"Template errors: {[f'{e.message} at {list(e.path)}' for e in errors or []]}",
    )
