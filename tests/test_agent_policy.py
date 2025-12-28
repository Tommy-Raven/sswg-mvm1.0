from __future__ import annotations

from generator.agent_policy import find_prohibited_commands, is_prohibited_command
from tests.assertions import require


def test_prohibited_command_detection() -> None:
    require(is_prohibited_command("ls -R"), "Expected ls -R to be prohibited")
    require(
        is_prohibited_command("grep -R pattern file"),
        "Expected grep -R to be prohibited",
    )
    require(not is_prohibited_command("ls -a"), "Expected ls -a to be allowed")


def test_find_prohibited_commands_filters_list() -> None:
    commands = ["ls -R", "ls -a", "grep -R foo bar"]
    prohibited = find_prohibited_commands(commands)
    require(
        prohibited == ["ls -R", "grep -R foo bar"],
        "Expected only prohibited commands to be returned",
    )
