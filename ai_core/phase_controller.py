#!/usr/bin/env python3
"""
ai_core/phase_controller.py — Phase-level execution for SSWG MVM.

The PhaseController is responsible for:

- Selecting modules that belong to a given phase.
- Resolving their execution order via the dependency graph.
- Executing each module with a shared context.
- Merging results back into the Workflow.

Contract (MVM):

- Module implementations are callables of the form:

    def my_module(context: dict) -> dict | None:
        ...

  They *may* also be async:

    async def my_async_module(context: dict) -> dict | None:
        ...

- Returned dicts are merged into the workflow context.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Iterable, List, Optional

from ai_monitoring.structured_logger import log_event

from .dependency_graph import CoreDependencyGraph
from .module_registry import ModuleRegistry, ModuleEntry
from .workflow import Workflow

logger = logging.getLogger("ai_core.phase_controller")
logger.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(_handler)


class PhaseController:
    """
    Orchestrates execution of modules within a single phase.
    """

    def __init__(self, module_registry: Optional[ModuleRegistry] = None) -> None:
        self.module_registry = module_registry or ModuleRegistry()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def run_phase(self, workflow: Workflow, phase_id: str) -> None:
        """
        Execute all modules associated with a given phase.

        Steps:
        - Fetch module *configs* for the phase from the workflow.
        - Compute a dependency-safe order via CoreDependencyGraph.
        - Execute modules in order, updating workflow context.
        """
        wf_id = workflow.id
        modules = workflow.get_modules_for_phase(phase_id)
        if not modules:
            logger.info(
                "No modules defined for phase %s in workflow %s", phase_id, wf_id
            )
            return

        logger.info(
            "Running phase %s for workflow %s with %d module(s)",
            phase_id,
            wf_id,
            len(modules),
        )

        # Build graph and determine execution order
        graph = CoreDependencyGraph(modules)
        ordered_modules = graph.topological_order()

        ctx = workflow.get_context()

        for mod_def in ordered_modules:
            module_id = mod_def.get("module_id")
            if not module_id:
                logger.warning(
                    "Skipping malformed module definition (no module_id) in phase %s",
                    phase_id,
                )
                continue

            entry = self.module_registry.get(module_id)
            if entry is None:
                logger.warning(
                    "No implementation registered for module %s (phase=%s, wf=%s)",
                    module_id,
                    phase_id,
                    wf_id,
                )
                log_event(
                    "phase.module_missing_impl",
                    {"workflow_id": wf_id, "phase": phase_id, "module_id": module_id},
                )
                continue

            log_event(
                "phase.module_started",
                {"workflow_id": wf_id, "phase": phase_id, "module_id": module_id},
            )

            success = True
            try:
                result = _execute_module(entry, ctx)
                if isinstance(result, dict):
                    # Merge returned data into context
                    workflow.update_context(result)
                    ctx.update(result)
            except Exception as e:
                success = False
                logger.error("Module %s in phase %s failed: %s", module_id, phase_id, e)
                log_event(
                    "phase.module_error",
                    {
                        "workflow_id": wf_id,
                        "phase": phase_id,
                        "module_id": module_id,
                        "error": str(e),
                    },
                )

            log_event(
                "phase.module_completed",
                {
                    "workflow_id": wf_id,
                    "phase": phase_id,
                    "module_id": module_id,
                    "success": success,
                },
            )

            # For MVM, we keep going even if one module fails; orchestrator
            # can decide at a higher level whether to treat this as fatal.

    # Potential extension: a future run_phase_async to integrate with
    # a fully async orchestrator variant.
    # For MVM, we stick to a sync interface + async-aware module execution.


# ---------------------------------------------------------------------- #
# Internal module execution helpers
# ---------------------------------------------------------------------- #
def _execute_module(entry: ModuleEntry, context: Dict[str, Any]) -> Any:
    """
    Execute a single module function (sync or async).

    Contract:
    - Module functions accept a single argument: context dict.
    - They may be declared async or return an awaitable.
    - They may return:
        - dict   → merged into context
        - None   → ignored
        - other  → left to caller to interpret (MVM ignores)
    """
    func = entry.func

    # If declared as async
    if asyncio.iscoroutinefunction(func):  # type: ignore[arg-type]
        return asyncio.run(func(context))  # type: ignore[arg-type]

    # If sync, call it
    result = func(context)  # type: ignore[arg-type]

    # If it returned a coroutine, await it
    if asyncio.iscoroutine(result):
        return asyncio.run(result)

    return result


# End of ai_core/phase_controller.py
