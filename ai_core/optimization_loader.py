#!/usr/bin/env python3
"""Optimization ontology loader for sswg-mvm."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

_DEFAULT_PATHS = (
    Path("data/templates/system_optimization_training_framework.json"),
    Path("data/templates/system_optimization_template.json"),
)


@lru_cache(maxsize=4)
def _load_from_path(path_str: str) -> Dict[str, Any]:
    path = Path(path_str)
    return json.loads(path.read_text(encoding="utf-8"))


def load_optimization_map(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load the optimization ontology JSON from disk."""
    if path is not None:
        return _load_from_path(str(path))

    for candidate in _DEFAULT_PATHS:
        if candidate.exists():
            return _load_from_path(str(candidate))

    raise FileNotFoundError(
        "No optimization ontology found in default template locations."
    )
