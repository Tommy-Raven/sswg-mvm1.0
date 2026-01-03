"""
generator/pdl_executor.py — Execute PDL-defined phases for runtime validation.

Loads a PDL YAML file, resolves handler paths, executes phases in order, and
emits a run report suitable for audit and telemetry.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Callable, Dict, List

import json
import yaml

from generator.hashing import hash_data
from generator.pdl_validator import validate_pdl_file


@dataclass
class PDLRunResult:
    """Result payload from a PDL execution run."""

    run_id: str
    report_path: Path
    phase_status: Dict[str, str]


def _load_pdl(path: Path) -> Dict[str, Any]:
    payload = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(payload)
    else:
        data = yaml.safe_load(payload)
    if not isinstance(data, dict):
        raise ValueError("PDL document must parse to a mapping object")
    return data


def _resolve_handler(handler_path: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
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


def _execute_phases(
    phases: List[Dict[str, Any]],
    *,
    context: Dict[str, Any],
) -> Dict[str, str]:
    phase_status: Dict[str, str] = {}
    for phase in phases:
        phase_name = phase.get("name", "unknown")
        handler_path = phase.get("handler", "")
        handler = _resolve_handler(handler_path)
        output = handler(context)
        if not isinstance(output, dict):
            raise ValueError(f"Handler output for {phase_name!r} must be a mapping.")
        context.update(output)
        phase_status[phase_name] = "complete"
    return phase_status


def execute_pdl_run(
    *,
    pdl_path: Path,
    report_dir: Path,
    run_id: str,
    initial_context: Dict[str, Any] | None = None,
    resolve_handlers: bool = True,
) -> PDLRunResult:
    """
    Execute a PDL file and emit a run report.

    Args:
        pdl_path: Path to the PDL YAML file.
        report_dir: Directory to emit run reports.
        run_id: Identifier for the run.
        initial_context: Optional starting context for phase execution.
        resolve_handlers: Validate handler resolution before execution.
    """
    validate_pdl_file(pdl_path, resolve_handlers=resolve_handlers)
    pdl_obj = _load_pdl(pdl_path)
    phases = pdl_obj.get("phases", [])
    if not isinstance(phases, list):
        raise ValueError("PDL phases must be a list")

    context: Dict[str, Any] = {
        "run_id": run_id,
        "inputs_hash": hash_data({"pdl": str(pdl_path)}),
        "phase_status": {},
        "artifacts": {},
    }
    if initial_context:
        context.update(initial_context)

    phase_status = _execute_phases(phases, context=context)
    context["phase_status"] = phase_status

    report_dir.mkdir(parents=True, exist_ok=True)
    report_payload = {
        "anchor": {
            "anchor_id": "pdl_runtime_report",
            "anchor_version": "1.0.0",
            "scope": "runtime",
            "owner": "generator.pdl_executor",
            "status": "draft",
        },
        "run_id": run_id,
        "pdl_path": str(pdl_path),
        "pdl_hash": hash_data(pdl_obj),
        "inputs_hash": context["inputs_hash"],
        "phase_status": phase_status,
        "outputs": context.get("artifacts", {}),
    }
    report_path = report_dir / f"pdl_run_{context['inputs_hash']}.json"
    report_path.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
    return PDLRunResult(
        run_id=run_id, report_path=report_path, phase_status=phase_status
    )
