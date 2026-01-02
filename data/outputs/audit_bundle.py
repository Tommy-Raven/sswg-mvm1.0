"""Audit bundle outputs for the sswg/mvm golden path."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

from generator.audit_bundle import build_bundle as _build_bundle
from generator.audit_bundle import load_audit_spec
from generator.audit_bundle import validate_bundle as _validate_bundle


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _extract_series(payload: Dict[str, Any], key: str) -> List[float]:
    if isinstance(payload.get(key), list):
        return [float(value) for value in payload[key]]
    history = payload.get("history")
    if isinstance(history, dict) and isinstance(history.get(key), list):
        return [float(value) for value in history[key]]
    metrics = payload.get("metrics")
    if isinstance(metrics, dict) and isinstance(metrics.get(key), list):
        return [float(value) for value in metrics[key]]
    return []


def _mean(values: Iterable[float]) -> float:
    values_list = list(values)
    if not values_list:
        return 0.0
    return round(sum(values_list) / len(values_list), 4)


def _entropy_totals(values: Iterable[float]) -> Dict[str, float]:
    values_list = list(values)
    return {
        "total": round(sum(values_list), 4),
        "mean": _mean(values_list),
    }


def _manifest_checksum(manifest: Dict[str, Any]) -> str:
    payload = {key: value for key, value in manifest.items() if key != "checksum"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return _sha256_bytes(encoded)


def _load_benchmark_log(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_audit_bundle(
    *,
    spec: Dict[str, Any],
    run_id: str,
    bundle_dir: Path,
    manifest_path: Path,
    benchmark_log_path: Path,
) -> Dict[str, Any]:
    """Create a bundle of audit artifacts with benchmark-derived metrics."""
    if not benchmark_log_path.exists():
        raise FileNotFoundError(f"Benchmark log missing: {benchmark_log_path}")

    base_manifest = _build_bundle(
        spec=spec,
        run_id=run_id,
        bundle_dir=bundle_dir,
        manifest_path=manifest_path,
    )

    benchmark_log = _load_benchmark_log(benchmark_log_path)
    entropy_values = _extract_series(benchmark_log, "entropy")
    verity_values = _extract_series(benchmark_log, "verity")

    manifest = dict(base_manifest)
    anchor = dict(manifest.get("anchor", {}))
    anchor["owner"] = "data.outputs.audit_bundle"
    manifest["anchor"] = anchor
    manifest["timestamp"] = _utc_timestamp()
    manifest["benchmark_log"] = {
        "path": str(benchmark_log_path),
        "checksum": _sha256_file(benchmark_log_path),
    }
    manifest["entropy_totals"] = _entropy_totals(entropy_values)
    manifest["verity_mean"] = _mean(verity_values)
    manifest["checksum"] = _manifest_checksum(manifest)

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def validate_audit_bundle(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Validate audit bundle manifest completeness and integrity."""
    results = _validate_bundle(manifest)
    errors = list(results.get("errors", []))

    required_fields = ["timestamp", "entropy_totals", "verity_mean", "checksum"]
    for field in required_fields:
        if field not in manifest:
            errors.append({"type": "missing_field", "field": field})

    benchmark = manifest.get("benchmark_log", {})
    benchmark_path = Path(benchmark.get("path", "")) if benchmark else None
    if benchmark_path and benchmark_path.exists():
        checksum = benchmark.get("checksum")
        if checksum and checksum != _sha256_file(benchmark_path):
            errors.append({"type": "benchmark_checksum_mismatch"})
    else:
        errors.append({"type": "benchmark_log_missing"})

    status = "pass" if not errors else "fail"
    return {"status": status, "errors": errors}


__all__ = [
    "build_audit_bundle",
    "load_audit_spec",
    "validate_audit_bundle",
]
