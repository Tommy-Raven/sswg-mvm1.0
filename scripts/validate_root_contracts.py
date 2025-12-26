#!/usr/bin/env python3
"""Validate root contract yaml files against json schemas."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, RefResolver


SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"
ROOT_DIR = Path(__file__).resolve().parent.parent


CONTRACTS = {
    "sswg.yaml": "sswg_contract_schema.json",
    "mvm.yaml": "mvm_contract_schema.json",
    "execution_policy.yaml": "execution_policy_schema.json",
    "governance.yaml": "governance_schema.json",
    "invariants.yaml": "invariants_schema.json",
    "root_contract.yaml": "root_contract_schema.json",
}


def load_schema(schema_name: str) -> dict:
    schema_path = SCHEMAS_DIR / schema_name
    return yaml.safe_load(schema_path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def get_validator(schema_name: str) -> Draft202012Validator:
    schema = load_schema(schema_name)
    base_uri = SCHEMAS_DIR.as_uri().rstrip("/") + "/"
    resolver = RefResolver(base_uri=base_uri, referrer=schema)
    return Draft202012Validator(schema, resolver=resolver)


def validate_contracts() -> int:
    failures: list[str] = []

    for yaml_name, schema_name in CONTRACTS.items():
        yaml_path = ROOT_DIR / yaml_name
        if not yaml_path.exists():
            failures.append(f"missing file: {yaml_name}")
            continue

        validator = get_validator(schema_name)
        data = load_yaml(yaml_path)
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if errors:
            for error in errors:
                path = "/".join(str(part) for part in error.path)
                failures.append(f"{yaml_name}: {path or '<root>'}: {error.message}")

    if failures:
        print("root contract validation failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("root contract validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(validate_contracts())
