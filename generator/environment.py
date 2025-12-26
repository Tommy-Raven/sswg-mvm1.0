from __future__ import annotations

import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from importlib import metadata

from generator.failure_emitter import FailureLabel
from generator.hashing import hash_data


def load_environment_lock(lock_path: Path) -> Dict[str, Any]:
    return json.loads(lock_path.read_text(encoding="utf-8"))


def compute_lock_hash(lock_path: Path) -> str:
    payload = load_environment_lock(lock_path)
    return hash_data(payload)


def get_git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def environment_fingerprint(lock_path: Path, container_tag: str | None = None) -> Dict[str, Any]:
    return {
        "os": platform.system(),
        "arch": platform.machine(),
        "python_version": sys.version.split()[0],
        "dependency_lock_hash": compute_lock_hash(lock_path),
        "git_commit": get_git_commit(),
        "container_tag": container_tag or "unknown",
    }


def check_environment_drift(lock_path: Path) -> FailureLabel | None:
    lock = load_environment_lock(lock_path)
    runtime = lock.get("runtime", {})
    expected_python = runtime.get("python_version")
    current_python = sys.version.split()[0]
    drift: Dict[str, Any] = {}
    if expected_python and expected_python != current_python:
        drift["python_version"] = {"expected": expected_python, "actual": current_python}

    missing: List[Dict[str, str]] = []
    mismatched: List[Dict[str, str]] = []
    for dependency in lock.get("dependencies", []):
        name = dependency.get("name")
        expected_version = dependency.get("version")
        if not name or not expected_version:
            continue
        try:
            actual_version = metadata.version(name)
        except metadata.PackageNotFoundError:
            missing.append({"name": name, "expected": expected_version})
            continue
        if actual_version != expected_version:
            mismatched.append(
                {
                    "name": name,
                    "expected": expected_version,
                    "actual": actual_version,
                }
            )

    if missing or mismatched:
        drift["dependencies"] = {"missing": missing, "mismatched": mismatched}

    if drift:
        return FailureLabel(
            Type="reproducibility_failure",
            message="Environment drift detected against dependency lock",
            phase_id="validate",
            evidence=drift,
        )

    return None
