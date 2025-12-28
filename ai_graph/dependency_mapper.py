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
from pathlib import Path
from typing import Any, Dict, List, Iterable

import yaml

logger = logging.getLogger("ai_graph.dependency_graph")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)

GRAPH_LIMITS_PATH = Path("config/graph_limits.yml")
DEFAULT_GRAPH_LIMITS = {
    "max_nodes": 1000,
    "max_edges": 5000,
    "enforce": True,
}


def _load_graph_limits(path: Path = GRAPH_LIMITS_PATH) -> Dict[str, Any]:
    if not path.exists():
        logger.warning("Graph limits config missing at %s; using defaults.", path)
        return dict(DEFAULT_GRAPH_LIMITS)

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("graph_limits.yml must contain a mapping at the top level.")

    limits = payload.get("graph_limits", {})
    if not isinstance(limits, dict):
        raise ValueError("graph_limits must be a mapping.")

    max_nodes = limits.get("max_nodes", DEFAULT_GRAPH_LIMITS["max_nodes"])
    max_edges = limits.get("max_edges", DEFAULT_GRAPH_LIMITS["max_edges"])
    enforce = limits.get("enforce", DEFAULT_GRAPH_LIMITS["enforce"])

    if not isinstance(max_nodes, int) or max_nodes <= 0:
        raise ValueError("graph_limits.max_nodes must be a positive integer.")
    if not isinstance(max_edges, int) or max_edges <= 0:
        raise ValueError("graph_limits.max_edges must be a positive integer.")
    if not isinstance(enforce, bool):
        raise ValueError("graph_limits.enforce must be a boolean.")

    return {"max_nodes": max_nodes, "max_edges": max_edges, "enforce": enforce}


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
        self._graph_limits = _load_graph_limits()
        self._enforce_graph_limits()
        self.adj = defaultdict(list)  # reverse adjacency: dep -> [dependents]
        for mid, m in self.modules.items():
            deps = m.get("dependencies", []) or []
            for d in deps:
                self.adj[d].append(mid)

    def _enforce_graph_limits(self) -> None:
        if not self._graph_limits.get("enforce", True):
            return

        node_count = len(self.modules)
        edge_count = sum(
            len(m.get("dependencies", []) or []) for m in self.modules.values()
        )
        max_nodes = self._graph_limits["max_nodes"]
        max_edges = self._graph_limits["max_edges"]

        if node_count > max_nodes or edge_count > max_edges:
            raise ValueError(
                "Dependency graph exceeds limits: "
                f"nodes {node_count}/{max_nodes}, edges {edge_count}/{max_edges}."
            )

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
            logger.warning(
                "Dependency cycle detected (visited=%d, total=%d).",
                visited,
                len(self.modules),
            )
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
                logger.warning(
                    "Removing missing dependencies for %s: %s", mid, sorted(removed)
                )
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

        logger.warning(
            "Cycle detected; attempting autocorrect using optional dependencies."
        )
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
                    logger.info(
                        "Autocorrect: removing optional dependency %s from %s", d, mid
                    )
                    optional_removed = True
                else:
                    newdeps.append(d)

            if optional_removed:
                m["dependencies"] = newdeps
                if not self.detect_cycle():
                    logger.info("Cycle resolved by removing optional dependencies.")
                    return True

        # Strategy 2: fallback: drop last-listed dependency across modules
        logger.warning(
            "Optional dependency removal insufficient; trying fallback strategy."
        )
        for mid, m in self.modules.items():
            deps = list(m.get("dependencies", []) or [])
            while deps:
                removed = deps.pop()
                logger.info(
                    "Fallback autocorrect: removing dependency %s from %s", removed, mid
                )
                m["dependencies"] = deps
                if not self.detect_cycle():
                    logger.info("Cycle resolved via fallback removal.")
                    return True

        logger.error("Autocorrect failed; cycle still present.")
        return False


# End of ai_graph/dependency_graph.py
