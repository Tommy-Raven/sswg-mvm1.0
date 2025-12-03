#!/usr/bin/env python3
"""
generator/plugin_loader.py — Dynamic plugin loading for SSWG generator.

This module provides minimal utilities to load external Python modules or
callables by dotted path for experiment-specific extensions.
"""

from __future__ import annotations

import importlib
from typing import Any


def load_object(dotted_path: str) -> Any:
    """
    Load an object given a dotted path, e.g.:
        "my_package.my_module:my_function"
        "my_package.my_module.MyClass"

    Returns the resolved object or raises ImportError / AttributeError.
    """
    if ":" in dotted_path:
        module_path, attr_name = dotted_path.split(":", 1)
    else:
        parts = dotted_path.rsplit(".", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid dotted path: {dotted_path!r}")
        module_path, attr_name = parts

    module = importlib.import_module(module_path)
    try:
        return getattr(module, attr_name)
    except AttributeError as err:
        raise AttributeError(f"{attr_name!r} not found in {module_path!r}") from err
