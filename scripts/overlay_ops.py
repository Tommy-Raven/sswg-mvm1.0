from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


class OverlayOperationError(RuntimeError):
    pass


def _decode_pointer_token(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def _resolve_pointer(container: Any, pointer: str) -> tuple[Any, str]:
    if not pointer.startswith("/"):
        raise OverlayOperationError(f"Invalid JSON pointer: {pointer}")
    tokens = [
        _decode_pointer_token(token)
        for token in pointer.lstrip("/").split("/")
        if token
    ]
    if not tokens:
        raise OverlayOperationError(f"Pointer must target a value: {pointer}")
    current = container
    for token in tokens[:-1]:
        if isinstance(current, list):
            try:
                index = int(token)
            except ValueError as exc:
                raise OverlayOperationError(
                    f"Expected list index in pointer: {pointer}"
                ) from exc
            if index >= len(current):
                raise OverlayOperationError(f"Pointer index out of range: {pointer}")
            current = current[index]
        elif isinstance(current, dict):
            if token not in current:
                raise OverlayOperationError(
                    f"Pointer path missing key '{token}': {pointer}"
                )
            current = current[token]
        else:
            raise OverlayOperationError(
                f"Pointer traversed non-container at {token}: {pointer}"
            )
    return current, tokens[-1]


def apply_operation(payload: Any, operation: dict[str, Any]) -> Any:
    op = operation.get("op")
    path = operation.get("path")
    if not op or not path:
        raise OverlayOperationError("Overlay operation requires op and path")
    container, last_token = _resolve_pointer(payload, path)
    if isinstance(container, list):
        try:
            index = int(last_token)
        except ValueError as exc:
            raise OverlayOperationError(
                f"Expected list index in pointer: {path}"
            ) from exc
        if index >= len(container):
            raise OverlayOperationError(f"Pointer index out of range: {path}")
        current_value = container[index]
        if op in {"add", "override"}:
            container[index] = operation.get("value")
        elif op == "deprecate":
            container[index] = {"deprecated": True, "previous": current_value}
        else:
            raise OverlayOperationError(f"Unknown operation: {op}")
    elif isinstance(container, dict):
        current_value = container.get(last_token)
        if op in {"add", "override"}:
            container[last_token] = operation.get("value")
        elif op == "deprecate":
            if last_token not in container:
                raise OverlayOperationError(
                    f"Pointer path missing key '{last_token}': {path}"
                )
            container[last_token] = {"deprecated": True, "previous": current_value}
        else:
            raise OverlayOperationError(f"Unknown operation: {op}")
    else:
        raise OverlayOperationError(f"Pointer resolved to non-container at {path}")
    return payload


def apply_overlays(payload: Any, overlays: list[dict[str, Any]]) -> Any:
    result = payload
    for overlay in overlays:
        for operation in overlay.get("operations", []):
            result = apply_operation(result, operation)
    return result


def load_artifact(path: Path) -> dict[str, Any]:
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise OverlayOperationError(f"Artifact at {path} must be a mapping")
    return data


def load_overlays(overlays_dir: Path) -> list[dict[str, Any]]:
    overlays = []
    if overlays_dir.exists():
        overlays = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(overlays_dir.glob("*.json"))
        ]
    overlays.sort(
        key=lambda overlay: (
            overlay.get("precedence", {}).get("order") is None,
            overlay.get("precedence", {}).get("order", 0),
            overlay.get("overlay_id", ""),
        )
    )
    return overlays


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
