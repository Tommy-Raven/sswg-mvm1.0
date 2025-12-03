#!/usr/bin/env python3
"""
ai_core package — Core orchestration primitives for SSWG MVM.

This package is responsible for:
- Defining the core workflow data model
- Orchestrating phase execution
- Managing module registration and dependency resolution
- Exposing a CLI-friendly entry surface (via ai_core.cli)

At MVM stage, we keep the public surface small and stable while allowing
internal evolution of implementations.
"""

from __future__ import annotations

from .workflow import Workflow
from .module_registry import ModuleRegistry
from .phase_controller import PhaseController
from .orchestrator import Orchestrator

__all__ = [
    "Workflow",
    "ModuleRegistry",
    "PhaseController",
    "Orchestrator",
]


def get_version() -> str:
    """
    Return a simple version identifier for the core orchestration subsystem.
    """
    return "ai_core-mvm-0.1.0"
