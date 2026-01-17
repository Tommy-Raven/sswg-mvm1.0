#!/usr/bin/env python3
"""
directive_core_validator.py

Canonical governance ingestion and enforcement validator for SSWG/MVM.

This validator enforces:
- Governance ingestion order
- Canonical TOML-only ledger headers
- Mandatory invariants
- Semantic Ambiguity Gate presence and wiring
- Fail-closed behavior on ambiguity or authority violations

This module MUST remain deterministic and side-effect free.
"""

from pathlib import Path
import tomllib
import re
import sys
from typing import List, Dict


# ============================================================
# Constants
# ============================================================

DIRECTIVE_ROOT = Path(__file__).resolve().parent
DOCS_DIR = DIRECTIVE_ROOT / "docs"
DEFINITIONS_DIR = DIRECTIVE_ROOT / "definitions"

REQUIRED_GOVERNANCE_ORDER = [
    "TERMINOLOGY.toml",
    "AGENTS.toml",
    "SSWG_CONSTITUTION.toml",
    "SECURITY_INVARIANTS.toml",
    "FORMAT_BOUNDARY_CONTRACT.toml",
    "ARCHITECTURE.toml",
    "FORMAL_GUARANTEES.toml",
    "REFERENCES.toml",
]

REQUIRED_AMBIGUITY_FILES = {
    "spec": DEFINITIONS_DIR / "ambiguity_gate_spec.toml",
    "invariant": DEFINITIONS_DIR / "ambiguity_gate_invariant.toml",
    "policy": DEFINITIONS_DIR / "ambiguity_gate.toml",
}

PUBLIC_ERROR_AMBIGUITY = "Semantic Ambiguity"
PUBLIC_ERROR_HEADER = "Invalid Canonical Header"
PUBLIC_ERROR_GOVERNANCE = "Governance Validation Failure"


# ============================================================
# Utilities
# ============================================================

def fail(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def load_toml(path: Path) -> Dict:
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except Exception:
        fail(f"{PUBLIC_ERROR_HEADER}: {path.name}")


# ============================================================
# Canonical Header Validation
# ============================================================

def validate_anchor(anchor: Dict, *, require_authority: bool | None = None) -> None:
    required_fields = {
        "anchor_id",
        "anchor_model",
        "anchor_version",
        "scope",
        "status",
        "authority",
        "owner",
        "init_purpose",
        "init_authors",
    }

    missing = required_fields - anchor.keys()
    if missing:
        fail(PUBLIC_ERROR_HEADER)

    if require_authority is not None:
        if anchor.get("authority") is not require_authority:
            fail(PUBLIC_ERROR_HEADER)


def validate_single_anchor(toml_data: Dict) -> Dict:
    if "anchor" not in toml_data:
        fail(PUBLIC_ERROR_HEADER)

    validate_anchor(toml_data["anchor"])
    return toml_data["anchor"]


# ============================================================
# Governance Ingestion Order
# ============================================================

def validate_governance_ingestion_order() -> None:
    present = sorted(
        p.name for p in DOCS_DIR.glob("*.toml")
        if p.name in REQUIRED_GOVERNANCE_ORDER
    )

    if present != REQUIRED_GOVERNANCE_ORDER[:len(present)]:
        fail(PUBLIC_ERROR_GOVERNANCE)


# ============================================================
# Ambiguity Gate Enforcement
# ============================================================

def load_ambiguity_gate() -> None:
    # Ensure all required files exist
    for path in REQUIRED_AMBIGUITY_FILES.values():
        if not path.exists():
            fail(PUBLIC_ERROR_GOVERNANCE)

    # Load and validate anchors
    spec = load_toml(REQUIRED_AMBIGUITY_FILES["spec"])
    inv = load_toml(REQUIRED_AMBIGUITY_FILES["invariant"])
    policy = load_toml(REQUIRED_AMBIGUITY_FILES["policy"])

    validate_single_anchor(spec)
    validate_anchor(inv.get("anchor", {}), require_authority=True)
    validate_anchor(policy.get("anchor", {}), require_authority=True)

    # Spec MUST be non-authoritative
    if spec["anchor"].get("authority") is not False:
        fail(PUBLIC_ERROR_GOVERNANCE)

    # Invariant + policy MUST be authoritative
    if not inv["anchor"].get("authority"):
        fail(PUBLIC_ERROR_GOVERNANCE)

    if not policy["anchor"].get("authority"):
        fail(PUBLIC_ERROR_GOVERNANCE)

    # Policy MUST define triggers
    triggers = policy.get("trigger")
    if not triggers or not isinstance(triggers, list):
        fail(PUBLIC_ERROR_GOVERNANCE)

    # Compile regexes to ensure determinism and validity
    for trig in triggers:
        pattern = trig.get("pattern")
        if not pattern:
            fail(PUBLIC_ERROR_GOVERNANCE)
        try:
            re.compile(pattern, re.IGNORECASE)
        except re.error:
            fail(PUBLIC_ERROR_GOVERNANCE)


# ============================================================
# YAML / Markdown Leakage Guard
# ============================================================

def validate_no_yaml_ledgers() -> None:
    illegal = list(DOCS_DIR.glob("*.md")) + list(DOCS_DIR.glob("*.yaml")) + list(DOCS_DIR.glob("*.yml"))
    if illegal:
        fail(PUBLIC_ERROR_GOVERNANCE)


# ============================================================
# Entry Point
# ============================================================

def run() -> None:
    validate_governance_ingestion_order()
    validate_no_yaml_ledgers()
    load_ambiguity_gate()


if __name__ == "__main__":
    run()
    
