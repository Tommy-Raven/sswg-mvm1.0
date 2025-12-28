from __future__ import annotations

import json
from pathlib import Path

from generator.anchor_registry import AnchorRegistry, enforce_anchor
from tests.assertions import require


def test_anchor_enforcement_detects_canonical_mutation(tmp_path: Path) -> None:
    registry_path = tmp_path / "anchor_registry.json"
    registry = AnchorRegistry(registry_path)
    artifact_path = tmp_path / "artifact.json"
    artifact = json.loads(Path("tests/fixtures/canonical_artifact.json").read_text(encoding="utf-8"))
    artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    failure = enforce_anchor(
        artifact_path=artifact_path,
        metadata=artifact["anchor"],
        registry=registry,
    )
    require(failure is None, "Expected no failure for initial canonical artifact")

    artifact["payload"]["field"] = "new-value"
    artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    failure = enforce_anchor(
        artifact_path=artifact_path,
        metadata=artifact["anchor"],
        registry=registry,
    )
    require(failure is not None, "Expected failure for canonical mutation")
    require(
        failure.Type == "reproducibility_failure",
        "Expected reproducibility_failure for canonical mutation",
    )
