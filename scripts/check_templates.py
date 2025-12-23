#!/usr/bin/env python3

"""Validate template files against the schema definition."""

from pathlib import Path
import json

from ai_validation.schema_validator import validate_template

meta_tpl = json.loads(
    Path("data/templates/meta_reflection_template.json").read_text(encoding="utf-8")
)
ok, errors = validate_template(meta_tpl)

if not ok:
    for e in errors or []:
        print("Template error:", e.message, "at", list(e.path))
else:
    print("meta_reflection_template.json is valid.")
