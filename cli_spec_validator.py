"""CLI entrypoint that delegates to cli_spec_validator_core."""

from __future__ import annotations

from cli.cli_spec_validator_core import main as core_main


def _main() -> int:
    return core_main()


if __name__ == "__main__":
    raise SystemExit(_main())
