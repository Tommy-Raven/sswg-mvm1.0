"""
Tests the SSWG CLI entrypoint.
"""

import sys
from subprocess import run as subprocess_run

from tests.assertions import require


def test_cli_help():
    result = subprocess_run(  # nosec B603
        [sys.executable, "-m", "generator.main", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    require(result.returncode == 0, "Expected CLI help command to succeed")
    require(
        "SSWG Workflow Generator" in result.stdout,
        "Expected CLI help output to include banner",
    )
