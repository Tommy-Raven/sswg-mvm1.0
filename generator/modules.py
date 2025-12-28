#!/usr/bin/env python3
"""
generator/modules.py — Generator-local module registry.

This is a light-weight registry specifically for generator-time modules:
small functions or callables that transform a workflow context.

It is intentionally simpler than ai_core.module_registry and can be used
by recursive expansion, semantic scoring, or custom pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


ModuleFunc = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class GeneratorModule:
    """Descriptor for a generator-time module."""

    name: str
    description: str
    run: ModuleFunc


class GeneratorModuleRegistry:
    """
    Simple in-memory registry for generator modules.

    Usage:
        registry = GeneratorModuleRegistry()
        registry.register("refine_objective", "Refine user objective", func)
        result = registry.run("refine_objective", context)
    """

    def __init__(self) -> None:
        self._modules: Dict[str, GeneratorModule] = {}

    def register(
        self,
        name: str,
        description: str,
        func: ModuleFunc,
        overwrite: bool = False,
    ) -> None:
        """Register a new module under the given name."""
        if not overwrite and name in self._modules:
            raise ValueError(f"Module {name!r} already registered")
        self._modules[name] = GeneratorModule(
            name=name,
            description=description,
            run=func,
        )

    def get(self, name: str) -> Optional[GeneratorModule]:
        """Return a module descriptor by name, if present."""
        return self._modules.get(name)

    def run(self, name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a registered module with the given context.

        Raises KeyError if the module is unknown.
        """
        module = self.get(name)
        if module is None:
            raise KeyError(f"Unknown generator module: {name}")
        return module.run(context)

    def list_modules(self) -> Dict[str, str]:
        """
        Return a mapping of name → description for discoverability.
        """
        return {name: module.description for name, module in self._modules.items()}
