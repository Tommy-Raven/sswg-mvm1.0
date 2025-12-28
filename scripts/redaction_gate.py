from __future__ import annotations

import argparse
import re
from pathlib import Path

from generator.failure_emitter import FailureEmitter, FailureLabel


DISALLOWED_PATTERNS = [
    re.compile(r"password\s*[:=]", re.IGNORECASE),
    re.compile(r"secret\s*[:=]", re.IGNORECASE),
    re.compile(r"token\s*[:=]", re.IGNORECASE),
    re.compile(r"api_key\s*[:=]", re.IGNORECASE),
    re.compile(r"credential\s*[:=]", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan generated artifacts for disallowed content."
    )
    parser.add_argument(
        "--scan-dirs",
        type=Path,
        nargs="+",
        default=[Path("artifacts"), Path("data")],
        help="Directories to scan for redaction violations.",
    )
    parser.add_argument(
        "--run-id", type=str, default="redaction-scan", help="Run identifier."
    )
    return parser.parse_args()


def _scan_file(path: Path) -> list[str]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return []
    hits = []
    for pattern in DISALLOWED_PATTERNS:
        if pattern.search(content):
            hits.append(pattern.pattern)
    return hits


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/redaction/failures"))
    violations = []

    for scan_dir in args.scan_dirs:
        if not scan_dir.exists():
            continue
        for path in scan_dir.rglob("*"):
            if path.is_dir():
                continue
            matches = _scan_file(path)
            if matches:
                violations.append({"path": str(path), "patterns": matches})

    if violations:
        emitter.emit(
            FailureLabel(
                Type="reproducibility_failure",
                message="Redaction scan detected disallowed content",
                phase_id="validate",
                evidence={"violations": violations},
            ),
            run_id=args.run_id,
        )
        print("Redaction gate failed")
        return 1

    print("Redaction gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
