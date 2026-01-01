"""Semantic network helpers for graph-based analyses."""

from __future__ import annotations

from typing import Any, Dict


def integrate_cross_domain_relations(
    graph: Any, mapping_relations: Dict[str, str]
) -> None:
    """
    Attach cross-domain analogy edges to an existing graph object.

    The graph object is expected to expose an `add_edge(source, target, **attrs)`
    method compatible with networkx-style interfaces.
    """
    if not mapping_relations:
        return

    for physical, computational in mapping_relations.items():
        graph.add_edge(physical, computational, relation="analogy")
