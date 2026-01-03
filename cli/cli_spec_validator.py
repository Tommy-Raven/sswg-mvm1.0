"""CLI entrypoint that delegates to cli_spec_validator_core."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cli.cli_spec_validator_core import main as core_main


def _main() -> int:
    return core_main()


if __name__ == "__main__":
    raise SystemExit(_main())
