from __future__ import annotations

import json
from pathlib import Path

from generator.secret_scanner import load_allowlist, scan_paths
from tests.assertions import require


def test_secret_scanner_flags_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("TOKEN=secret", encoding="utf-8")
    results = scan_paths([tmp_path], allowlist=[])
    require(results["violations"], "Expected secret scanner violations")


def test_secret_scanner_respects_allowlist(tmp_path: Path) -> None:
    secret_file = tmp_path / "artifact.txt"
    secret_file.write_text("token=secret", encoding="utf-8")
    allowlist_path = tmp_path / "allowlist.json"
    allowlist_path.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "entry_id": "allow-1",
                        "path_glob": str(secret_file),
                        "pattern": "(?i)token\\s*[:=]",
                        "scope": "tests",
                        "expires_at": "2999-01-01T00:00:00Z",
                        "approved_by": "security",
                        "approval_ref": "remediation-15",
                        "allow_on_canonical": False,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    allowlist = load_allowlist(allowlist_path)
    results = scan_paths([tmp_path], allowlist=allowlist)
    require(not results["violations"], "Expected allowlist to suppress violations")
