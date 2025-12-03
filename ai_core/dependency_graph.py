#!/usr/bin/env python3
"""
ai_core/dependency_graph.py — Core-level dependency wrapper for SSWG MVM.

This is a thin adapter around `ai_graph.dependency_mapper.DependencyGraph`
tailored to the needs of ai_core:

- Accepts a list of module dicts (with `module_id` and `dependencies`).
- Provides:
    - `detect_cycle()`
    - `autocorrect_missing_dependencies()`
    - `attempt_autocorrect_cycle()`
    - `topological_order()` — for execution ordering in PhaseController.

ai_core code should import from here instead of directly from ai_graph so
the underlying implementation can evolve without breaking callers.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List

from ai_graph.dependency_mapper import DependencyGraph as _GraphImpl

logger = logging.getLogger("ai_core.dependency_graph")
logger.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(_handler)


class CoreDependencyGraph:
    """
    Core-facing dependency graph wrapper.

    Modules are expected to be dicts with at least:
      - "module_id": str
      - "dependencies": list[str] (optional)
    """

    def __init__(self, modules: Iterable[Dict[str, Any]]) -> None:
        self._modules: List[Dict[str, Any]] = list(modules)
        self._impl = _GraphImpl(self._modules)

    def detect_cycle(self) -> bool:
        return self._impl.detect_cycle()

    def autocorrect_missing_dependencies(self) -> None:
        self._impl.autocorrect_missing_dependencies()

    def attempt_autocorrect_cycle(self) -> bool:
        return self._impl.attempt_autocorrect_cycle()

    def topological_order(self) -> List[Dict[str, Any]]:
        """
        Return modules in a dependency-safe order for execution.

        Strategy:
        - Use the underlying graph's cycle detection and autocorrect.
        - If a cycle cannot be resolved, return modules in their original order
          but log a warning; PhaseController may still choose to run them in
          this degraded mode.
        """
        self.autocorrect_missing_dependencies()
        if self.detect_cycle():
            logger.warning(
                "Unresolved cycle in CoreDependencyGraph; returning original order."
            )
            return self._modules

        # We have to reconstruct order because the underlying implementation
        # doesn't expose a baked topological sort; we reimplement a small one
        # here using the cleaned module set.

        modules_by_id = {m["module_id"]: m for m in self._modules}
        indeg = {mid: 0 for mid in modules_by_id}

        for mid, m in modules_by_id.items():
            deps = m.get("dependencies", []) or []
            for d in deps:
                if d in indeg:
                    indeg[mid] += 1

        # Kahn's algorithm
        from collections import deque

        q = deque([mid for mid, d in indeg.items() if d == 0])
        ordered_ids: List[str] = []

        while q:
            mid = q.popleft()
            ordered_ids.append(mid)
            for dep_mid, m in modules_by_id.items():
                if mid in (m.get("dependencies", []) or []):
                    indeg[dep_mid] -= 1
                    if indeg[dep_mid] == 0:
                        q.append(dep_mid)

        if len(ordered_ids) != len(modules_by_id):
            logger.warning(
                "Topological sort did not cover all modules; falling back to original order."
            )
            return self._modules

        return [modules_by_id[mid] for mid in ordered_ids]
# ----------------------------------------------------------------------