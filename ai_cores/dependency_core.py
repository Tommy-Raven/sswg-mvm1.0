#!/usr/bin/env python3
"""
ai_cores/dependency_core.py — Canonical dependency graph utilities for SSWG MVM.

Provides deterministic dependency resolution and cycle correction.
"""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml

logger = logging.getLogger("ai_cores.dependency_core")
logger.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(_handler)

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
        for mid, module in self.modules.items():
            deps = module.get("dependencies", []) or []
            for dep in deps:
                self.adj[dep].append(mid)

    def _enforce_graph_limits(self) -> None:
        if not self._graph_limits.get("enforce", True):
            return

        node_count = len(self.modules)
        edge_count = sum(
            len(module.get("dependencies", []) or [])
            for module in self.modules.values()
        )
        max_nodes = self._graph_limits["max_nodes"]
        max_edges = self._graph_limits["max_edges"]

        if node_count > max_nodes or edge_count > max_edges:
            raise ValueError(
                "Dependency graph exceeds limits: "
                f"nodes {node_count}/{max_nodes}, edges {edge_count}/{max_edges}."
            )

    def detect_cycle(self) -> bool:
        """
        Detect whether the current dependency structure contains a cycle.

        Uses a variant of Kahn's algorithm. Returns True if a cycle exists.
        """
        indeg = {module_id: 0 for module_id in self.modules}
        for src, module in self.modules.items():
            for dep in module.get("dependencies", []) or []:
                if dep in indeg:
                    indeg[src] += 1

        queue = deque([node for node, degree in indeg.items() if degree == 0])
        visited = 0

        while queue:
            node = queue.popleft()
            visited += 1
            for neighbor in self.adj.get(node, []):
                indeg[neighbor] -= 1
                if indeg[neighbor] == 0:
                    queue.append(neighbor)

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

    def autocorrect_missing_dependencies(self) -> None:
        """Remove dependencies that refer to non-existent modules."""
        for module_id, module in self.modules.items():
            deps = list(module.get("dependencies", []) or [])
            cleaned = [dep for dep in deps if dep in self.modules]
            removed = set(deps) - set(cleaned)
            if removed:
                logger.warning(
                    "Removing missing dependencies for %s: %s",
                    module_id,
                    sorted(removed),
                )
                module["dependencies"] = cleaned

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
        for module_id, module in self.modules.items():
            deps = list(module.get("dependencies", []) or [])
            if not deps:
                continue

            optional_removed = False
            newdeps: List[str] = []
            for dep in deps:
                dep_obj = self.modules.get(dep, {})
                if dep_obj.get("dependency_optional", False):
                    logger.info(
                        "Autocorrect: removing optional dependency %s from %s",
                        dep,
                        module_id,
                    )
                    optional_removed = True
                else:
                    newdeps.append(dep)

            if optional_removed:
                module["dependencies"] = newdeps
                if not self.detect_cycle():
                    logger.info("Cycle resolved by removing optional dependencies.")
                    return True

        logger.warning(
            "Optional dependency removal insufficient; trying fallback strategy."
        )
        for module_id, module in self.modules.items():
            deps = list(module.get("dependencies", []) or [])
            while deps:
                removed = deps.pop()
                logger.info(
                    "Fallback autocorrect: removing dependency %s from %s",
                    removed,
                    module_id,
                )
                module["dependencies"] = deps
                if not self.detect_cycle():
                    logger.info("Cycle resolved via fallback removal.")
                    return True

        logger.error("Autocorrect failed; cycle still present.")
        return False
