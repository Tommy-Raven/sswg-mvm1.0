from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from generator.hashing import hash_data


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate promotion checklist artifact.")
    parser.add_argument("--promotion-id", type=str, required=True, help="Promotion identifier.")
    parser.add_argument(
        "--evidence-paths",
        type=Path,
        nargs="+",
        required=True,
        help="Evidence artifact paths.",
    )
    parser.add_argument("--approver-id", type=str, required=True, help="Approver identifier.")
    parser.add_argument("--role", type=str, required=True, help="Approver role.")
    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path("artifacts/governance/promotion_checklist.json"),
        help="Output checklist path.",
    )
    parser.add_argument(
        "--decision",
        type=str,
        choices=["approve", "reject"],
        default="approve",
        help="Promotion decision.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    evidence = []
    for path in args.evidence_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        evidence.append({"path": str(path), "hash": hash_data(payload)})

    checklist = {
        "anchor": {
            "anchor_id": "promotion_checklist",
            "anchor_version": "1.0.0",
            "scope": "promotion",
            "owner": "scripts.generate_promotion_checklist",
            "status": "draft",
        },
        "promotion_id": args.promotion_id,
        "promotion_decision": args.decision,
        "evidence": evidence,
        "approvals": [
            {
                "approver_id": args.approver_id,
                "role": args.role,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ],
    }

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(json.dumps(checklist, indent=2), encoding="utf-8")
    print(f"Promotion checklist written to {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
