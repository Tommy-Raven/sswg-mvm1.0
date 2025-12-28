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
    "guarantees.yaml": "guarantees_schema.json",
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

    root_contract_path = ROOT_DIR / "root_contract.yaml"
    invariants_path = ROOT_DIR / "invariants.yaml"
    if root_contract_path.exists() and invariants_path.exists():
        root_contract = load_yaml(root_contract_path)
        invariants_doc = load_yaml(invariants_path)
        root_invariants = root_contract.get("root_contract", {}).get("invariants")
        invariants_source = root_contract.get("root_contract", {}).get(
            "invariants_source"
        )
        canonical_invariants = invariants_doc.get("invariants")

        if invariants_source != "invariants.yaml":
            failures.append(
                "root_contract.yaml: root_contract/invariants_source must be invariants.yaml"
            )

        if not isinstance(root_invariants, list) or not isinstance(
            canonical_invariants, list
        ):
            failures.append(
                "root_contract.yaml: invariants must be a list in both files"
            )
        else:
            root_map = {item.get("id"): item.get("rule") for item in root_invariants}
            canonical_map = {
                item.get("id"): item.get("rule") for item in canonical_invariants
            }
            if root_map != canonical_map:
                failures.append(
                    "root_contract.yaml: invariants do not match invariants.yaml"
                )

    if failures:
        print("root contract validation failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    cross_failures = _validate_output_guarantees()
    if cross_failures:
        print("root contract cross-validation failures:")
        for failure in cross_failures:
            print(f"- {failure}")
        return 1

    print("root contract validation passed")
    return 0


def _validate_output_guarantees() -> list[str]:
    failures: list[str] = []
    execution_policy = load_yaml(ROOT_DIR / "execution_policy.yaml")
    guarantees = load_yaml(ROOT_DIR / "guarantees.yaml")

    tooling = execution_policy.get("execution_policy", {}).get("tooling", {})
    required_guarantees = set(tooling.get("required_output_guarantees", []))
    defined_guarantees = set(
        guarantees.get("guarantees", {}).get("definitions", {}).keys()
    )
    missing = required_guarantees - defined_guarantees
    if missing:
        failures.append(
            "execution_policy.yaml: tooling.required_output_guarantees must be defined "
            f"in guarantees.yaml (missing: {', '.join(sorted(missing))})"
        )

    guarantees_ref = tooling.get("guarantees_ref")
    if guarantees_ref and not (ROOT_DIR / guarantees_ref).exists():
        failures.append(
            "execution_policy.yaml: tooling.guarantees_ref does not exist "
            f"({guarantees_ref})"
        )

    return failures


if __name__ == "__main__":
    raise SystemExit(validate_contracts())
