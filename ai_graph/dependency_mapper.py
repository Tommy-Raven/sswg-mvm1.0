#!/usr/bin/env python3
"""
ai_graph/dependency_graph.py — Dependency graph utilities for SSWG MVM.

This module builds and analyzes a simple module dependency graph:

- Detects cycles using Kahn's algorithm
- Removes missing dependencies (modules that don't exist)
- Attempts to autocorrect cycles by:
  - first removing optional dependencies (dependency_optional=True)
  - then, as a fallback, removing the last listed dependency

It's intentionally conservative and deterministic so it can be used
safely in CI and during early MVM experimentation.
"""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from typing import Any, Dict, List, Iterable

logger = logging.getLogger("ai_graph.dependency_graph")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


class DependencyGraph:
    """
    Represents a directed graph of module dependencies.

    Modules are expected to be dicts with at least:
      - module_id: str
      - dependencies: list[str] (optional)
      - dependency_optional: bool (optional flag on dependents)
    """

    def __init__(self, modules: Iterable[Dict[str, Any]]):
        self.modules: Dict[str, Dict[str, Any]] = {m["module_id"]: m for m in modules}
        self.adj = defaultdict(list)  # reverse adjacency: dep -> [dependents]
        for mid, m in self.modules.items():
            deps = m.get("dependencies", []) or []
            for d in deps:
                self.adj[d].append(mid)

    # ------------------------------------------------------------------ #
    # Core Graph Checks
    # ------------------------------------------------------------------ #
    def detect_cycle(self) -> bool:
        """
        Detect whether the current dependency structure contains a cycle.

        Uses a variant of Kahn's algorithm. Returns True if a cycle exists.
        """
        indeg = {mid: 0 for mid in self.modules}
        # compute indegrees based on dependencies
        for src, m in self.modules.items():
            for d in m.get("dependencies", []) or []:
                if d in indeg:
                    indeg[src] += 1

        q = deque([n for n, d in indeg.items() if d == 0])
        visited = 0

        while q:
            n = q.popleft()
            visited += 1
            for nbr in self.adj.get(n, []):
                indeg[nbr] -= 1
                if indeg[nbr] == 0:
                    q.append(nbr)

        # cycle if not all nodes were visited
        has_cycle = visited != len(self.modules)
        if has_cycle:
            logger.warning("Dependency cycle detected (visited=%d, total=%d).", visited, len(self.modules))
        else:
            logger.info("No dependency cycle detected.")
        return has_cycle

    # ------------------------------------------------------------------ #
    # Autocorrect Utilities
    # ------------------------------------------------------------------ #
    def autocorrect_missing_dependencies(self) -> None:
        """
        Remove dependencies that refer to non-existent modules.
        """
        for mid, m in self.modules.items():
            deps = list(m.get("dependencies", []) or [])
            cleaned = [d for d in deps if d in self.modules]
            removed = set(deps) - set(cleaned)
            if removed:
                logger.warning("Removing missing dependencies for %s: %s", mid, sorted(removed))
                m["dependencies"] = cleaned

    def attempt_autocorrect_cycle(self) -> bool:
        """
        Attempt to resolve cycles using simple heuristics:

        1. Try removing dependencies from modules that mark them as optional
           via dependency_optional=True.
        2. As a fallback, remove the last-listed dependency from modules until
           the graph becomes acyclic.

        Returns:
            bool: True if a correction succeeded, False otherwise.
        """
        if not self.detect_cycle():
            return False

        logger.warning("Cycle detected; attempting autocorrect using optional dependencies.")
        # Strategy 1: try remove optional dependencies
        for mid, m in self.modules.items():
            deps = list(m.get("dependencies", []) or [])
            if not deps:
                continue

            optional_removed = False
            newdeps: List[str] = []
            for d in deps:
                dep_obj = self.modules.get(d, {})
                if dep_obj.get("dependency_optional", False):
                    logger.info("Autocorrect: removing optional dependency %s from %s", d, mid)
                    optional_removed = True
                else:
                    newdeps.append(d)

            if optional_removed:
                m["dependencies"] = newdeps
                if not self.detect_cycle():
                    logger.info("Cycle resolved by removing optional dependencies.")
                    return True

        # Strategy 2: fallback: drop last-listed dependency across modules
        logger.warning("Optional dependency removal insufficient; trying fallback strategy.")
        for mid, m in self.modules.items():
            deps = list(m.get("dependencies", []) or [])
            while deps:
                removed = deps.pop()
                logger.info("Fallback autocorrect: removing dependency %s from %s", removed, mid)
                m["dependencies"] = deps
                if not self.detect_cycle():
                    logger.info("Cycle resolved via fallback removal.")
                    return True

        logger.error("Autocorrect failed; cycle still present.")
        return False
# End of ai_graph/dependency_graph.py