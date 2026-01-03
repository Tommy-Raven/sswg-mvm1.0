#!/usr/bin/env python3
"""
ai_conductor/module_registry.py — Module registry for SSWG MVM.

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

Core storage utilities live in ai_cores.module_core.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Optional

from ai_monitoring.structured_logger import log_event
from ai_cores.module_core import ModuleEntry, ModuleFunc, ModuleRegistryCore

logger = logging.getLogger("ai_conductor.module_registry")
logger.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(_handler)


class ModuleRegistry(ModuleRegistryCore):
    """
    In-memory registry of modules used by the ai_conductor orchestrator.

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
        super().__init__()

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
        entry = super().register(
            module_id=module_id,
            func=func,
            phase_id=phase_id,
            inputs=inputs,
            outputs=outputs,
            description=description,
            metadata=metadata,
            overwrite=True,
        )

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
        return super().get(module_id)

    def require(self, module_id: str) -> ModuleEntry:
        """
        Retrieve a module entry by id, raising if not found.
        """
        return super().require(module_id)

    def list_modules(self) -> List[ModuleEntry]:
        """
        Return all registered module entries.
        """
        return super().list_modules()

    def list_by_phase(self, phase_id: str) -> List[ModuleEntry]:
        """
        Return all modules that belong to the given phase_id.
        """
        return super().list_by_phase(phase_id)
