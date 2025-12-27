from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from generator.failure_emitter import FailureLabel
from generator.hashing import hash_data

ALLOWED_STATUSES = {"draft", "sandbox", "canonical", "archived"}


@dataclass(frozen=True)
class AnchorRecord:
    anchor_id: str
    anchor_version: str
    scope: str
    owner: str
    status: str
    path: str
    content_hash: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "anchor_id": self.anchor_id,
            "anchor_version": self.anchor_version,
            "scope": self.scope,
            "owner": self.owner,
            "status": self.status,
            "path": self.path,
            "content_hash": self.content_hash,
        }


class AnchorRegistry:
    def __init__(self, registry_path: Path) -> None:
        self.registry_path = registry_path
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.registry_path.exists():
            self.registry_path.write_text(
                json.dumps({"anchor_registry_version": "1.0.0", "anchors": []}, indent=2),
                encoding="utf-8",
            )

    def load(self) -> Dict[str, Any]:
        return json.loads(self.registry_path.read_text(encoding="utf-8"))

    def save(self, data: Dict[str, Any]) -> None:
        self.registry_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def register(self, record: AnchorRecord) -> None:
        data = self.load()
        anchors = data.get("anchors", [])
        for anchor in anchors:
            if anchor["anchor_id"] == record.anchor_id:
                if anchor["anchor_version"] == record.anchor_version:
                    raise ValueError(
                        f"Duplicate anchor_id/version: {record.anchor_id}@{record.anchor_version}"
                    )
        anchors.append(record.as_dict())
        data["anchors"] = anchors
        self.save(data)

    def find(self, anchor_id: str, anchor_version: str) -> Optional[Dict[str, Any]]:
        data = self.load()
        for anchor in data.get("anchors", []):
            if anchor["anchor_id"] == anchor_id and anchor["anchor_version"] == anchor_version:
                return anchor
        return None


def validate_anchor_metadata(metadata: Dict[str, Any]) -> None:
    required = {"anchor_id", "anchor_version", "scope", "owner", "status"}
    missing = required - metadata.keys()
    if missing:
        raise ValueError(f"Missing anchor fields: {sorted(missing)}")
    if metadata["status"] not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid anchor status: {metadata['status']}")


def enforce_anchor(
    *,
    artifact_path: Path,
    metadata: Dict[str, Any],
    registry: AnchorRegistry,
) -> Optional[FailureLabel]:
    validate_anchor_metadata(metadata)
    artifact_payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    content_hash = hash_data(artifact_payload)
    existing = registry.find(metadata["anchor_id"], metadata["anchor_version"])
    if existing and existing["status"] == "canonical":
        if existing["content_hash"] != content_hash:
            return FailureLabel(
                Type="reproducibility_failure",
                message="Canonical anchor mutation detected",
                phase_id="validate",
                evidence={
                    "anchor_id": metadata["anchor_id"],
                    "anchor_version": metadata["anchor_version"],
                    "path": str(artifact_path),
                },
            )
    if not existing:
        record = AnchorRecord(
            anchor_id=metadata["anchor_id"],
            anchor_version=metadata["anchor_version"],
            scope=metadata["scope"],
            owner=metadata["owner"],
            status=metadata["status"],
            path=str(artifact_path),
            content_hash=content_hash,
        )
        registry.register(record)
    return None
