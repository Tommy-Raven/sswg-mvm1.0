"""Audit bundle creation and validation helpers."""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from generator.hashing import hash_data


@dataclass(frozen=True)
class BundleEntry:
    """Entry for an audited bundle artifact."""

    component_id: str
    source_path: Path
    bundle_path: Path
    content_hash: str


def load_audit_spec(path: Path) -> Dict[str, Any]:
    """Load the audit bundle specification from disk."""
    return json.loads(path.read_text(encoding="utf-8"))


def _hash_file(path: Path) -> str:
    """Hash file contents using SHA-256."""
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _resolve_components(spec: Dict[str, Any], run_id: str) -> List[dict]:
    """Resolve spec component paths for the provided run ID."""
    components = []
    for component in spec.get("components", []):
        if "path_template" in component:
            path = component["path_template"].format(run_id=run_id)
            components.append(
                {"component_id": component["component_id"], "paths": [path]}
            )
        elif "path_glob" in component:
            paths = sorted(Path(".").glob(component["path_glob"]))
            components.append(
                {
                    "component_id": component["component_id"],
                    "paths": [str(path) for path in paths],
                }
            )
    return components


def build_bundle(
    *,
    spec: Dict[str, Any],
    run_id: str,
    bundle_dir: Path,
    manifest_path: Path,
) -> Dict[str, Any]:
    """Create a bundle of audit artifacts and emit a manifest."""
    bundle_dir.mkdir(parents=True, exist_ok=True)
    entries: List[BundleEntry] = []

    for component in _resolve_components(spec, run_id):
        component_id = component["component_id"]
        for source in component.get("paths", []):
            source_path = Path(source)
            if not source_path.exists():
                continue
            target_dir = bundle_dir / component_id
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / source_path.name
            shutil.copy2(source_path, target_path)
            entries.append(
                BundleEntry(
                    component_id=component_id,
                    source_path=source_path,
                    bundle_path=target_path,
                    content_hash=_hash_file(target_path),
                )
            )

    manifest = {
        "anchor": {
            "anchor_id": "audit_bundle_manifest",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "generator.audit_bundle",
            "status": "draft",
        },
        "run_id": run_id,
        "bundle_dir": str(bundle_dir),
        "entries": [
            {
                "component_id": entry.component_id,
                "source_path": str(entry.source_path),
                "bundle_path": str(entry.bundle_path),
                "content_hash": entry.content_hash,
            }
            for entry in entries
        ],
    }
    manifest["bundle_hash"] = hash_data(manifest["entries"])
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def validate_bundle(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a bundle manifest against on-disk artifacts."""
    errors = []
    entries = manifest.get("entries", [])
    run_id = manifest.get("run_id")
    overlay_chain = None
    inputs_hash = None

    for entry in entries:
        bundle_path = Path(entry.get("bundle_path", ""))
        if not bundle_path.exists():
            errors.append({"type": "missing_bundle_path", "path": str(bundle_path)})
            continue
        content_hash = _hash_file(bundle_path)
        if content_hash != entry.get("content_hash"):
            errors.append({"type": "hash_mismatch", "path": str(bundle_path)})
        if bundle_path.suffix == ".json":
            try:
                payload = json.loads(bundle_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if run_id and payload.get("run_id") not in (None, run_id):
                errors.append(
                    {
                        "type": "run_id_mismatch",
                        "path": str(bundle_path),
                        "value": payload.get("run_id"),
                    }
                )
            if "overlay_chain" in payload:
                if overlay_chain is None:
                    overlay_chain = payload.get("overlay_chain")
                elif overlay_chain != payload.get("overlay_chain"):
                    errors.append(
                        {
                            "type": "overlay_chain_mismatch",
                            "path": str(bundle_path),
                        }
                    )
            if "inputs_hash" in payload:
                if inputs_hash is None:
                    inputs_hash = payload.get("inputs_hash")
                elif inputs_hash != payload.get("inputs_hash"):
                    errors.append(
                        {
                            "type": "inputs_hash_mismatch",
                            "path": str(bundle_path),
                        }
                    )

    status = "pass" if not errors else "fail"
    return {"status": status, "errors": errors}
