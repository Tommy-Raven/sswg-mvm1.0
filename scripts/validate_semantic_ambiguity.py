#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict, Any, Tuple

ERROR_LABEL = "Semantic Ambiguity"

# Minimal semver (X.Y.Z) for anchor_version where applicable
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")

# Conservative ambiguity triggers: deterministic + intentionally strict.
# You can extend these over time, but MUST NOT weaken them silently.
from typing import List, Tuple
import re

# ---------------------------------------------------------------------
# Semantic Ambiguity Detection Patterns
# Ambiguity is treated as a security vulnerability.
# Any match SHALL trigger fail-closed governance rejection.
# ---------------------------------------------------------------------

AMBIGUITY_PATTERNS: List[Tuple[str, re.Pattern]] = [
    # Authority & intent ambiguity
    (
        "implied_authority_language",
        re.compile(r"\b(implied|implicitly|assumed|should be considered)\b", re.IGNORECASE),
    ),
    (
        "interpretive_permission_language",
        re.compile(r"\b(may be interpreted as|reasonable interpretation|common sense)\b", re.IGNORECASE),
    ),
    (
        "roleplay_or_trusted_intent",
        re.compile(r"\b(trusted intent|acting as|roleplay)\b", re.IGNORECASE),
    ),

    # Operational / procedural leakage
    (
        "operational_instruction_language",
        re.compile(
            r"\b(step[- ]by[- ]step|procedure|do this next|follow these steps)\b",
            re.IGNORECASE,
        ),
    ),

    # Meta-instruction and circumvention tactics
    (
        "meta_instruction_loopholes",
        re.compile(
            r"\b(you know what I mean|wink wink|if you catch my drift)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "delegated_agency_language",
        re.compile(
            r"\b(on behalf of|instructed by|was told to)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "plausible_deniability_phrases",
        re.compile(
            r"\b(just an example|hypothetically|just saying)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "simulated_decisionmaking",
        re.compile(
            r"\b(let's assume|in a scenario where|imagine if)\b",
            re.IGNORECASE,
        ),
    ),

    # Specification laundering / authority smuggling
    (
        "technical_implication_loopholes",
        re.compile(
            r"\b(as defined in RFC|per the specification|under .* standard)\b",
            re.IGNORECASE,
        ),
    ),

    # Nested / hidden instruction attempts
    (
        "nested_instruction_language",
        re.compile(
            r"\b(inside this request|embedded in this message|read between the lines)\b",
            re.IGNORECASE,
        ),
    ),

    # Semantic fuzzing and relativism
    (
        "semantic_confusion_tactics",
        re.compile(
            r"\b(technically speaking|arguably|from a certain point of view)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "contextual_exceptions",
        re.compile(
            r"\b(except in this case|unique situation|special condition)\b",
            re.IGNORECASE,
        ),
    ),

    # Pseudo-legal / policy laundering
    (
        "pseudo_legal_language",
        re.compile(
            r"\b(within the bounds of|in accordance with|under the clause)\b",
            re.IGNORECASE,
        ),
    ),
]


@dataclass(frozen=True)
class AmbiguityFinding:
    path: str
    rule_id: str
    message: str

class SemanticAmbiguityError(RuntimeError):
    def __init__(self, findings: List[AmbiguityFinding]):
        super().__init__(ERROR_LABEL)
        self.findings = findings

def emit_failure(path: Path, findings: List[AmbiguityFinding]) -> Dict[str, Any]:
    return {
        "Type": "semantic_ambiguity",
        "severity": "critical",
        "failure_behavior": "fail_closed",
        "message": "Semantic Ambiguity detected: ambiguity is a security vulnerability and SHALL be rejected.",
        "error_label": ERROR_LABEL,
        "affected_path": str(path),
        "findings": [f.__dict__ for f in findings],
        "remediation_required": True,
    }

def quarantine_append(quarantine_path: Path, payload: Dict[str, Any]) -> None:
    quarantine_path.parent.mkdir(parents=True, exist_ok=True)
    # JSONL for append-only auditability
    with quarantine_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=True) + "\n")

def detect_semantic_ambiguity(text: str, source_path: str) -> List[AmbiguityFinding]:
    findings: List[AmbiguityFinding] = []

    for rule_id, pattern in AMBIGUITY_PATTERNS:
        if pattern.search(text):
            findings.append(
                AmbiguityFinding(
                    path=source_path,
                    rule_id=rule_id,
                    message=f"Matched semantic ambiguity pattern: {rule_id}",
                )
            )

    return findings

def semantic_ambiguity_gate(
    candidate_paths: Iterable[Path],
    quarantine_registry_path: Path,
) -> List[Path]:
    """
    Returns the filtered candidate list (exiling ambiguous artifacts).
    On any ambiguity: fail-closed (raise), after writing quarantine record.
    """
    survivors: List[Path] = []
    all_findings: List[AmbiguityFinding] = []
    exiled: List[Path] = []

    for p in candidate_paths:
        if not p.exists() or not p.is_file():
            # Missing file is not ambiguity; let higher-level validators handle existence.
            survivors.append(p)
            continue

        try:
            text = p.read_text(encoding="utf-8", errors="strict")
        except Exception:
            # Unreadable is an ambiguity-class hazard; treat as fail-closed.
            finding = AmbiguityFinding(str(p), "unreadable_artifact", "Artifact unreadable; treated as semantic ambiguity hazard.")
            all_findings.append(finding)
            exiled.append(p)
            continue

        findings = detect_semantic_ambiguity(text, str(p))
        if findings:
            all_findings.extend(findings)
            exiled.append(p)
        else:
            survivors.append(p)

    if exiled:
        payload = {
            "Type": "semantic_ambiguity",
            "error_label": ERROR_LABEL,
            "exiled": [str(p) for p in exiled],
            "findings": [f.__dict__ for f in all_findings],
        }
        quarantine_append(quarantine_registry_path, payload)
        raise SemanticAmbiguityError(all_findings)

    return survivors

def main() -> int:
    # Your repo likely has a repo-root discovery helper already; use it here.
    # Placeholder: treat cwd as repo root.
    repo_root = Path.cwd().resolve()
    docs_dir = repo_root / "directive_core" / "docs"
    quarantine_path = repo_root / "directive_core" / "artifacts" / "audit" / "semantic_ambiguity_quarantine.jsonl"

    # Candidate governance artifacts: conservative default = all docs/*.toml
    candidates = sorted(docs_dir.glob("*.toml"))
    try:
        semantic_ambiguity_gate(candidates, quarantine_path)
    except SemanticAmbiguityError as e:
        # Print a stable JSON failure object for CI
        failure = emit_failure(docs_dir, e.findings)
        print(json.dumps(failure, sort_keys=True))
        return 2

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
