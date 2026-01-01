"""
SSWG PDL — Default Phase Definitions (Python)

Purpose:
    Provide a canonical placeholder for workflow phase definitions and
    utilities to load the default workflow spec (JSON-backed).
"""

from __future__ import annotations

import json
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Callable, Dict, Optional


_DEFAULT_JSON_PATH = Path(__file__).with_name("default-pdf.json")


def load_default_phases() -> Dict[str, Dict[str, Any]]:
    """
    Load the default set of workflow phases.

    Returns:
        Mapping of phase names to canonical definitions.
    """
    return {
        "ingest": {
            "description": "Collect and register raw inputs without interpretation.",
            "handler": "pdl.handlers.ingest",
            "inputs": [{"id": "raw_payload", "type": "blob"}],
            "outputs": [{"id": "ingested_payload", "type": "blob"}],
        },
        "normalize": {
            "description": "Normalize inputs into canonical forms.",
            "handler": "pdl.handlers.normalize",
            "inputs": [{"id": "ingested_payload", "type": "blob"}],
            "outputs": [{"id": "normalized_payload", "type": "blob"}],
        },
        "parse": {
            "description": "Bind normalized payloads to schema-aware structures.",
            "handler": "pdl.handlers.parse",
            "inputs": [{"id": "normalized_payload", "type": "blob"}],
            "outputs": [{"id": "parsed_payload", "type": "structured"}],
        },
        "analyze": {
            "description": "Compute deterministic measurements from parsed artifacts.",
            "handler": "pdl.handlers.analyze",
            "inputs": [{"id": "parsed_payload", "type": "structured"}],
            "outputs": [{"id": "analysis_metrics", "type": "metrics"}],
        },
        "generate": {
            "description": "Generate declarative outputs derived from analysis.",
            "handler": "pdl.handlers.generate",
            "inputs": [{"id": "analysis_metrics", "type": "metrics"}],
            "outputs": [{"id": "draft_output", "type": "artifact"}],
        },
        "validate": {
            "description": "Validate schemas and invariants on generated artifacts.",
            "handler": "pdl.handlers.validate",
            "inputs": [{"id": "draft_output", "type": "artifact"}],
            "outputs": [{"id": "validated_output", "type": "artifact"}],
        },
        "compare": {
            "description": "Compare outputs against baselines deterministically.",
            "handler": "pdl.handlers.compare",
            "inputs": [{"id": "validated_output", "type": "artifact"}],
            "outputs": [{"id": "comparison_report", "type": "report"}],
        },
        "interpret": {
            "description": "Interpret measured artifacts with labeled nondeterminism.",
            "handler": "pdl.handlers.interpret",
            "inputs": [{"id": "comparison_report", "type": "report"}],
            "outputs": [{"id": "interpretation_summary", "type": "summary"}],
        },
        "log": {
            "description": "Record run metadata, hashes, phase status, and persisted artifacts.",
            "handler": "pdl.handlers.log",
            "inputs": [{"id": "interpretation_summary", "type": "summary"}],
            "outputs": [{"id": "audit_log", "type": "log"}],
        },
    }


def _resolve_handler(handler_path: str) -> Callable[..., Dict[str, Any]]:
    module_path, _, attribute = handler_path.rpartition(".")
    if not module_path or not attribute:
        raise ValueError(f"Invalid handler path: {handler_path!r}")
    if find_spec(module_path) is None:
        raise ImportError(f"Handler module not found: {module_path!r}")
    module = import_module(module_path)
    handler = getattr(module, attribute, None)
    if handler is None or not callable(handler):
        raise AttributeError(f"Handler not callable: {handler_path!r}")
    return handler


def _validate_handlers(phases: Dict[str, Dict[str, Any]]) -> None:
    for phase_name, phase in phases.items():
        handler_path = phase.get("handler")
        if not handler_path:
            raise ValueError(f"Missing handler for phase: {phase_name}")
        _resolve_handler(handler_path)


def load_default_workflow_spec(path: Optional[str | Path] = None) -> Dict[str, Any]:
    """
    Load the default workflow spec from JSON.

    Args:
        path: Optional override path for the JSON spec. If omitted, the
              sibling file `default-pdf.json` is used.

    Returns:
        Parsed workflow spec dictionary.
    """
    spec_path = Path(path) if path is not None else _DEFAULT_JSON_PATH

    if not spec_path.exists():
        # Fallback: synthesize a spec using the known default phases.
        phases = list(load_default_phases().keys())
        return {
            "workflow": {
                "name": "default",
                "phases": phases,
            }
        }

    with spec_path.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def execute_phase(
    phase_name: str,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Execute a single default phase (placeholder).

    Args:
        phase_name:
            Name of the phase to execute.
        context:
            Optional context dictionary for phase execution. At MVM stage,
            this is only logged and not interpreted.
    """
    phase_definitions = load_default_phases()
    context = context or {}

    _validate_handlers(phase_definitions)

    if phase_name not in phase_definitions:
        available = ", ".join(sorted(phase_definitions.keys()))
        print(f"[PDL] Unknown phase: {phase_name!r}")
        print(f"[PDL] Available phases: {available}")
        return

    handler_path = phase_definitions[phase_name]["handler"]
    handler = _resolve_handler(handler_path)
    inputs = context.get("inputs") or context.get("last_output") or {}
    phase_output = handler(inputs, context=context)
    context["last_output"] = phase_output

    context_keys = ", ".join(sorted(context.keys()))
    print(
        f"[PDL] Executing default phase: {phase_name} "
        f"(context keys: {context_keys or 'none'})"
    )
