#!/usr/bin/env python3
"""
ai_core/module_registry.py — Module registry for SSWG MVM.

The ModuleRegistry is a lightweight in-memory store that maps `module_id`
to callable implementations and metadata.

Responsibilities (MVM):
- Register modules with:
    - module_id (string key)
    - callable (sync or async)
    - phase_id (optional)
    - inputs / outputs (optional, for documentation and wiring)
    - description / metadata
- Provide lookup and listing helpers.

This registry is intentionally dumb and local for now; in the future it
can be backed by a plugin system, config files, or remote service.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Union

from ai_monitoring.structured_logger import log_event

logger = logging.getLogger("ai_core.module_registry")
logger.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(_handler)

ModuleFunc = Union[Callable[..., Any], Callable[..., Awaitable[Any]]]


@dataclass
class ModuleEntry:
    """Descriptor for a registered module."""
    module_id: str
    func: ModuleFunc
    phase_id: Optional[str] = None
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ModuleRegistry:
    """
    In-memory registry of modules used by the ai_core orchestrator.

    Typical usage:

        registry = ModuleRegistry()
        registry.register(
            "m01_location_check",
            location_check_func,
            phase_id="phase_init",
            inputs=["context"],
            outputs=["location_valid", "permits_required"],
            description="Check if location and permits are valid.",
        )
        entry = registry.get("m01_location_check")
        result = entry.func(context)
    """

    def __init__(self) -> None:
        self._modules: Dict[str, ModuleEntry] = {}

    # ------------------------------------------------------------------ #
    # Registration
    # ------------------------------------------------------------------ #
    def register(
        self,
        module_id: str,
        func: ModuleFunc,
        *,
        phase_id: Optional[str] = None,
        inputs: Optional[Iterable[str]] = None,
        outputs: Optional[Iterable[str]] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a module implementation.

        Args:
            module_id: Unique identifier for the module.
            func: Callable that implements the module logic (sync or async).
            phase_id: Optional phase identifier this module belongs to.
            inputs: Optional list of input keys expected in the context.
            outputs: Optional list of output keys added to the context.
            description: Human-readable description.
            metadata: Arbitrary additional info.
        """
        entry = ModuleEntry(
            module_id=module_id,
            func=func,
            phase_id=phase_id,
            inputs=list(inputs or []),
            outputs=list(outputs or []),
            description=description,
            metadata=metadata or {},
        )
        self._modules[module_id] = entry

        logger.info("Registered module: %s (phase=%s)", module_id, phase_id)
        log_event(
            "module.register",
            {
                "module_id": module_id,
                "phase_id": phase_id,
                "inputs": entry.inputs,
                "outputs": entry.outputs,
            },
        )

    # ------------------------------------------------------------------ #
    # Lookup
    # ------------------------------------------------------------------ #
    def get(self, module_id: str) -> Optional[ModuleEntry]:
        """
        Retrieve a module entry by id.

        Returns:
            ModuleEntry or None if not found.
        """
        return self._modules.get(module_id)

    def require(self, module_id: str) -> ModuleEntry:
        """
        Retrieve a module entry by id, raising if not found.
        """
        entry = self.get(module_id)
        if entry is None:
            raise KeyError(f"Module not registered: {module_id}")
        return entry

    def list_modules(self) -> List[ModuleEntry]:
        """
        Return all registered module entries.
        """
        return list(self._modules.values())

    def list_by_phase(self, phase_id: str) -> List[ModuleEntry]:
        """
        Return all modules that belong to the given phase_id.
        """
        return [m for m in self._modules.values() if m.phase_id == phase_id]

    def __contains__(self, module_id: str) -> bool:
        return module_id in self._modules

    def __len__(self) -> int:
        return len(self._modules)
