from __future__ import annotations

from generator.agent_policy import find_prohibited_commands, is_prohibited_command


def test_prohibited_command_detection() -> None:
    assert is_prohibited_command("ls -R")
    assert is_prohibited_command("grep -R pattern file")
    assert not is_prohibited_command("ls -a")


def test_find_prohibited_commands_filters_list() -> None:
    commands = ["ls -R", "ls -a", "grep -R foo bar"]
    prohibited = find_prohibited_commands(commands)
    assert prohibited == ["ls -R", "grep -R foo bar"]
