from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver


def _get_validator(schema_path: Path) -> Draft202012Validator:
    schema_path = schema_path.resolve()
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    base_uri = schema_path.parent.as_uri().rstrip("/") + "/"
    return Draft202012Validator(schema, resolver=RefResolver(base_uri=base_uri, referrer=schema))


def test_overlay_descriptor_valid() -> None:
    validator = _get_validator(Path("schemas/overlay-descriptor.json"))
    overlay = json.loads(Path("tests/fixtures/overlay_descriptor.json").read_text(encoding="utf-8"))
    errors = list(validator.iter_errors(overlay))
    assert not errors
