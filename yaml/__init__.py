"""Minimal YAML loader for deterministic offline parsing."""

from __future__ import annotations

from typing import Any, List, Tuple


class YAMLError(Exception):
    """Raised when YAML parsing fails."""


def safe_load(text: str) -> Any:
    try:
        return _parse_yaml(text)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        raise YAMLError(str(exc)) from exc


def _parse_yaml(text: str) -> Any:
    lines = [line.rstrip("\n") for line in text.splitlines()]
    value, index = _parse_block(lines, 0, 0)
    _skip_empty(lines, index)
    return value


def _parse_block(lines: List[str], index: int, indent: int) -> Tuple[Any, int]:
    index = _skip_empty(lines, index)
    if index >= len(lines):
        return {}, index

    line = lines[index]
    if _indent_of(line) < indent:
        return {}, index

    if line[indent:].startswith("- "):
        return _parse_list(lines, index, indent)
    return _parse_dict(lines, index, indent)


def _parse_list(lines: List[str], index: int, indent: int) -> Tuple[List[Any], int]:
    items: List[Any] = []
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        line_indent = _indent_of(line)
        if line_indent < indent:
            break
        if line_indent > indent or not line[indent:].startswith("- "):
            break
        content = line[indent + 2 :].strip()
        index += 1
        if not content:
            item, index = _parse_block(lines, index, indent + 2)
            items.append(item)
            continue
        if ":" in content:
            key, value_part = content.split(":", 1)
            item: dict[str, Any] = {}
            value_part = value_part.strip()
            if value_part:
                item[key.strip()] = _parse_value(value_part)
            else:
                value, index = _parse_block(lines, index, indent + 2)
                item[key.strip()] = value
            while index < len(lines):
                next_line = lines[index]
                if not next_line.strip() or next_line.lstrip().startswith("#"):
                    index += 1
                    continue
                next_indent = _indent_of(next_line)
                if next_indent < indent + 2:
                    break
                if next_indent > indent + 2 or next_line[indent + 2 :].startswith("- "):
                    break
                key_part, value_part = next_line[indent + 2 :].split(":", 1)
                value_part = value_part.strip()
                index += 1
                if value_part:
                    item[key_part.strip()] = _parse_value(value_part)
                else:
                    value, index = _parse_block(lines, index, indent + 4)
                    item[key_part.strip()] = value
            items.append(item)
        else:
            items.append(_parse_value(content))
    return items, index


def _parse_dict(lines: List[str], index: int, indent: int) -> Tuple[dict[str, Any], int]:
    obj: dict[str, Any] = {}
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        line_indent = _indent_of(line)
        if line_indent < indent:
            break
        if line_indent > indent or line[indent:].startswith("- "):
            break
        if ":" not in line[indent:]:
            raise ValueError(f"Invalid mapping entry: {line}")
        key, value_part = line[indent:].split(":", 1)
        value_part = value_part.strip()
        index += 1
        if value_part:
            obj[key.strip()] = _parse_value(value_part)
        else:
            value, index = _parse_block(lines, index, indent + 2)
            obj[key.strip()] = value
    return obj, index


def _parse_value(value: str) -> Any:
    value = value.strip()
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "None"}:
        return None
    if (value.startswith("\"") and value.endswith("\"")) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        return int(value)
    try:
        return float(value)
    except ValueError:
        return value


def _skip_empty(lines: List[str], index: int) -> int:
    while index < len(lines):
        line = lines[index]
        if line.strip() and not line.lstrip().startswith("#"):
            break
        index += 1
    return index


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


__all__ = ["safe_load", "YAMLError"]
