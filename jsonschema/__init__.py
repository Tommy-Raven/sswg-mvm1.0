"""Minimal JSON Schema validation helpers for offline testing."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple
from urllib.parse import urlparse


class ValidationError(Exception):
    """Minimal validation error matching jsonschema's interface."""

    def __init__(
        self,
        message: str,
        path: Optional[List[Any]] = None,
        schema_path: Optional[List[Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.path = path or []
        self.schema_path = schema_path or []


@dataclass
class RefResolver:
    base_uri: str = ""
    referrer: Optional[Dict[str, Any]] = None
    store: Optional[Dict[str, Any]] = None

    def resolve(self, ref: str) -> Tuple[str, Dict[str, Any]]:
        schema = _resolve_ref_with_base(ref, self.base_uri, self.referrer, self.store)
        return ref, schema


class Draft202012Validator:
    """Minimal Draft 2020-12 validator used by tests."""

    def __init__(
        self, schema: Dict[str, Any], resolver: Optional[RefResolver] = None
    ) -> None:
        self.schema = schema
        self.resolver = resolver or RefResolver(referrer=schema)

    def iter_errors(self, instance: Any) -> Iterable[ValidationError]:
        return _iter_errors(instance, self.schema, [], [], self.resolver, self.schema)


def _iter_errors(
    instance: Any,
    schema: Dict[str, Any],
    path: List[Any],
    schema_path: List[Any],
    resolver: RefResolver,
    referrer: Optional[Dict[str, Any]],
) -> Iterator[ValidationError]:
    if "$ref" in schema:
        resolved, resolved_referrer = _resolve_ref(schema["$ref"], resolver, referrer)
        yield from _iter_errors(
            instance,
            resolved,
            path,
            schema_path + ["$ref"],
            resolver,
            resolved_referrer,
        )
        return

    if "allOf" in schema:
        for idx, subschema in enumerate(schema["allOf"]):
            yield from _iter_errors(
                instance,
                subschema,
                path,
                schema_path + ["allOf", idx],
                resolver,
                referrer,
            )

    if "const" in schema and instance != schema["const"]:
        yield ValidationError(
            f"{instance!r} is not equal to {schema['const']!r}",
            path,
            schema_path + ["const"],
        )
        return

    if "enum" in schema and instance not in schema["enum"]:
        yield ValidationError(
            f"{instance!r} is not one of {schema['enum']!r}",
            path,
            schema_path + ["enum"],
        )

    if "type" in schema and not _matches_type(instance, schema["type"]):
        yield ValidationError(
            f"{instance!r} is not of type '{schema['type']}'",
            path,
            schema_path + ["type"],
        )
        return

    if isinstance(instance, dict):
        yield from _validate_object(
            instance, schema, path, schema_path, resolver, referrer
        )
    elif isinstance(instance, list):
        yield from _validate_array(
            instance, schema, path, schema_path, resolver, referrer
        )
    elif isinstance(instance, str):
        pattern = schema.get("pattern")
        if pattern and re.match(pattern, instance) is None:
            yield ValidationError(
                f"{instance!r} does not match '{pattern}'",
                path,
                schema_path + ["pattern"],
            )


def _validate_object(
    instance: Dict[str, Any],
    schema: Dict[str, Any],
    path: List[Any],
    schema_path: List[Any],
    resolver: RefResolver,
    referrer: Optional[Dict[str, Any]],
) -> Iterator[ValidationError]:
    required = schema.get("required", [])
    for key in required:
        if key not in instance:
            yield ValidationError(
                f"'{key}' is a required property",
                path,
                schema_path + ["required"],
            )

    properties = schema.get("properties", {})
    for key, subschema in properties.items():
        if key in instance:
            yield from _iter_errors(
                instance[key],
                subschema,
                path + [key],
                schema_path + ["properties", key],
                resolver,
                referrer,
            )

    additional = schema.get("additionalProperties", True)
    if additional is False:
        for key in instance:
            if key not in properties:
                yield ValidationError(
                    f"Additional properties are not allowed ('{key}' was unexpected)",
                    path + [key],
                    schema_path + ["additionalProperties"],
                )
    elif isinstance(additional, dict):
        for key, value in instance.items():
            if key not in properties:
                yield from _iter_errors(
                    value,
                    additional,
                    path + [key],
                    schema_path + ["additionalProperties"],
                    resolver,
                    referrer,
                )

    min_props = schema.get("minProperties")
    if min_props is not None and len(instance) < min_props:
        yield ValidationError(
            f"{len(instance)} is less than the minimum of {min_props}",
            path,
            schema_path + ["minProperties"],
        )

    max_props = schema.get("maxProperties")
    if max_props is not None and len(instance) > max_props:
        yield ValidationError(
            f"{len(instance)} is greater than the maximum of {max_props}",
            path,
            schema_path + ["maxProperties"],
        )


def _validate_array(
    instance: List[Any],
    schema: Dict[str, Any],
    path: List[Any],
    schema_path: List[Any],
    resolver: RefResolver,
    referrer: Optional[Dict[str, Any]],
) -> Iterator[ValidationError]:
    min_items = schema.get("minItems")
    if min_items is not None and len(instance) < min_items:
        yield ValidationError(
            f"{len(instance)} is less than the minimum of {min_items}",
            path,
            schema_path + ["minItems"],
        )

    max_items = schema.get("maxItems")
    if max_items is not None and len(instance) > max_items:
        yield ValidationError(
            f"{len(instance)} is greater than the maximum of {max_items}",
            path,
            schema_path + ["maxItems"],
        )

    prefix_items = schema.get("prefixItems", [])
    for idx, subschema in enumerate(prefix_items):
        if idx >= len(instance):
            break
        yield from _iter_errors(
            instance[idx],
            subschema,
            path + [idx],
            schema_path + ["prefixItems", idx],
            resolver,
            referrer,
        )

    items_schema = schema.get("items")
    if items_schema is False:
        if len(instance) > len(prefix_items):
            yield ValidationError(
                "Additional items are not allowed",
                path,
                schema_path + ["items"],
            )
    elif isinstance(items_schema, dict):
        start = len(prefix_items)
        for idx in range(start, len(instance)):
            yield from _iter_errors(
                instance[idx],
                items_schema,
                path + [idx],
                schema_path + ["items"],
                resolver,
                referrer,
            )


def _matches_type(instance: Any, expected: Any) -> bool:
    if isinstance(expected, list):
        return any(_matches_type(instance, option) for option in expected)
    if expected == "object":
        return isinstance(instance, dict)
    if expected == "array":
        return isinstance(instance, list)
    if expected == "string":
        return isinstance(instance, str)
    if expected == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "boolean":
        return isinstance(instance, bool)
    return True


def _resolve_ref(
    ref: str, resolver: RefResolver, referrer: Optional[Dict[str, Any]]
) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    if ref.startswith("#"):
        if referrer is None:
            raise KeyError(f"Fragment {ref!r} not found in schema")
        return _resolve_fragment(referrer, ref[1:]), referrer
    return _resolve_ref_with_base(ref, resolver, referrer)


def _resolve_ref_with_base(
    ref: str,
    resolver: RefResolver,
    current_schema: Optional[Dict[str, Any]],
) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    if ref.startswith("#"):
        if current_schema is None:
            raise ValueError("No referrer available for local reference")
        return _resolve_fragment(current_schema, ref[1:]), current_schema

    base_root = _base_path_from_uri(resolver.base_uri)
    schema_base = (current_schema or {}).get("$id") or resolver.base_uri
    base_dir = _base_dir_from_uri(schema_base, base_root)

    path_part, fragment = _split_ref(ref)
    if path_part.startswith("http://") or path_part.startswith("https://"):
        parsed = urlparse(path_part)
        schema_path = base_root / parsed.path.lstrip("/")
    else:
        schema_path = base_root / base_dir / path_part

    if not schema_path.exists():
        alternate_root = base_root / "schemas"
        alternate_path = alternate_root / base_dir / path_part
        if alternate_path.exists():
            schema_path = alternate_path
        else:
            phase_path = base_root / "pdl-phases" / path_part
            if phase_path.exists():
                schema_path = phase_path
            else:
                alternate_phase_path = alternate_root / "pdl-phases" / path_part
                if alternate_phase_path.exists():
                    schema_path = alternate_phase_path

    schema = _load_schema(schema_path)
    if resolver.store:
        base_ref = path_part.rstrip("#")
        schema = resolver.store.get(base_ref, schema)

    if fragment:
        return _resolve_fragment(schema, fragment), schema
    return schema, schema


def _split_ref(ref: str) -> Tuple[str, str]:
    if "#" in ref:
        base, fragment = ref.split("#", 1)
        return base, fragment
    return ref, ""


def _resolve_fragment(schema: Dict[str, Any], fragment: str) -> Dict[str, Any]:
    if fragment.startswith("/"):
        fragment = fragment[1:]
    if not fragment:
        return schema
    node: Any = schema
    for part in fragment.split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            raise KeyError(f"Fragment {fragment!r} not found in schema")
    if not isinstance(node, dict):
        raise TypeError("Resolved fragment is not a schema object")
    return node


def _base_path_from_uri(base_uri: str) -> Path:
    if not base_uri:
        return Path.cwd()
    parsed = urlparse(base_uri)
    if parsed.scheme in {"", "file"}:
        return Path(parsed.path)
    return Path.cwd()


def _base_dir_from_uri(uri: str, base_root: Path) -> Path:
    parsed = urlparse(uri)
    path = Path(parsed.path)
    if parsed.scheme in {"", "file"}:
        if uri.endswith("/") or path.as_posix().endswith("/"):
            return Path(".")
        try:
            return path.parent.relative_to(base_root)
        except ValueError:
            return path.parent
    return Path(parsed.path.lstrip("/")).parent


def _load_schema(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


__all__ = ["Draft202012Validator", "RefResolver", "ValidationError"]
