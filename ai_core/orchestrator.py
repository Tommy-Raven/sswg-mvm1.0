#!/usr/bin/env python3

"""
ai_core/orchestrator.py — Core workflow orchestrator for SSWG MVM.

This is the *core* orchestration layer:

- It does NOT build workflows from prompts/configs (that lives in generator/).
- It assumes you already have a `Workflow` instance (schema-aligned dict wrapper).
- It coordinates:
    - phase execution (via PhaseController)
    - module dispatch (via ModuleRegistry)
    - validation (via ai_validation)
    - optional memory + telemetry + CLI dashboard hooks.

The older pattern:

    Orchestrator.run(user_config, recursive=False)

has effectively moved "up" to generator.main. Here we focus on:

    Orchestrator.run(workflow, phases=None)

where `workflow` is an ai_core.Workflow instance.
"""

from __future__ import annotations

import logging
from typing import Iterable, List, Optional

from ai_monitoring.structured_logger import log_event
from ai_validation import (
    apply_incident_metadata,
    build_incident,
    classify_exception,
    classify_validation_failure,
    recovery_decision,
    validate_workflow,
)

from .module_registry import ModuleRegistry
from .phase_controller import PhaseController
from .workflow import Workflow

logger = logging.getLogger("ai_core.orchestrator")
logger.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(_handler)

# Optional integrations — kept soft so MVM doesn't explode if not present
try:
    from ai_memory.memory_store import MemoryStore  # type: ignore
except Exception:  # pragma: no cover - defensive stub
    class MemoryStore:  # type: ignore[no-redef]
        def save(self, obj):
            return None


try:
    from ai_monitoring.cli_dashboard import CLIDashboard  # type: ignore
except Exception:  # pragma: no cover - defensive stub
    class CLIDashboard:  # type: ignore[no-redef]
        def record_cycle(self, success: bool) -> None:
            pass

        def record_phase(self, phase_id: str, success: bool) -> None:
            pass

        def render(self) -> None:
            pass


try:
    from ai_monitoring.telemetry import TelemetryLogger  # type: ignore
except Exception:  # pragma: no cover - defensive stub
    class TelemetryLogger:  # type: ignore[no-redef]
        def record(self, event: str, data=None) -> None:
            pass


class Orchestrator:
    """
    High-level conductor for multi-phase workflow execution.

    Usage (MVM):

        registry = ModuleRegistry()
        # ... register modules ...

        wf = Workflow(workflow_dict)
        orch = Orchestrator(module_registry=registry)
        orch.run(wf)               # run default phases
        orch.run(wf, phases=["init", "build"])  # subset
    """

    def __init__(
        self,
        module_registry: Optional[ModuleRegistry] = None,
        phase_controller: Optional[PhaseController] = None,
    ) -> None:
        self.module_registry = module_registry or ModuleRegistry()
        self.phase_controller = phase_controller or PhaseController(
            module_registry=self.module_registry
        )

        self.memory = MemoryStore()
        self.dashboard = CLIDashboard()
        self.telemetry = TelemetryLogger()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def run(
        self,
        workflow: Workflow,
        phases: Optional[Iterable[str]] = None,
        validate_after: bool = True,
    ) -> Workflow:
        """
        Run the given workflow through its phases.

        Args:
            workflow: Workflow instance to execute.
            phases: Optional subset of phase ids to run. If None, use
                    workflow.default_phases (or a sensible default).
            validate_after: If True, run schema validation at the end.

        Returns:
            The same Workflow instance, potentially mutated with outputs,
            evaluation results, etc.
        """
        wf_id = workflow.id
        phases_to_run: List[str] = list(
            phases or workflow.get_default_phases()
        )
        phase_status: dict[str, dict[str, object]] = {}

        logger.info("Starting orchestration for workflow %s", wf_id)
        log_event(
            "orchestrator.run.started",
            {"workflow_id": wf_id, "phases": phases_to_run},
        )
        self.telemetry.record("workflow_start", {"workflow_id": wf_id})

        # Run phases in order
        for phase_id in phases_to_run:
            logger.info("Running phase: %s", phase_id)
            log_event(
                "orchestrator.phase.started",
                {"workflow_id": wf_id, "phase": phase_id},
            )
            self.telemetry.record(
                "phase_start", {"workflow_id": wf_id, "phase": phase_id}
            )

            success = True
            failure_details = None
            try:
                self.phase_controller.run_phase(workflow, phase_id)
            except Exception as e:
                success = False
                failure_details = {
                    "Type": "deterministic_failure",
                    "message": str(e),
                }
                signal = classify_exception(e, source="phase_execution")
                decision = recovery_decision(signal.error_class, signal.severity)
                incident = build_incident(wf_id, signal)
                apply_incident_metadata(workflow.metadata, incident, decision)
                logger.error("Phase %s failed: %s", phase_id, e)
                phase_status[phase_id] = {
                    "status": "failed",
                    "failure": failure_details,
                }
                log_event(
                    "orchestrator.phase.error",
                    {
                        "workflow_id": wf_id,
                        "phase": phase_id,
                        "error": str(e),
                        "phase_status": {
                            phase_id: phase_status[phase_id]
                        },
                    },
                )
                self.telemetry.record(
                    "phase_error",
                    {"workflow_id": wf_id, "phase": phase_id, "error": str(e)},
                )

            if success:
                phase_status[phase_id] = {"status": "success"}

            self.dashboard.record_phase(phase_id, success=success)
            self.dashboard.record_cycle(success=success)

            log_event(
                "orchestrator.phase.completed",
                {
                    "workflow_id": wf_id,
                    "phase": phase_id,
                    "success": success,
                    "phase_status": dict(phase_status),
                },
            )
            self.telemetry.record(
                "phase_end",
                {"workflow_id": wf_id, "phase": phase_id, "success": success},
            )

            if not success:
                # For MVM, we just stop on first hard failure
                break

        # Optional validation
        if validate_after:
            wf_dict = workflow.to_dict()
            valid, errors = validate_workflow(wf_dict)
            if not valid:
                logger.error(
                    "Schema validation failed for workflow %s (%d issue(s)).",
                    wf_id,
                    len(errors or []),
                )
                signal = classify_validation_failure(len(errors or []))
                decision = recovery_decision(signal.error_class, signal.severity)
                incident = build_incident(wf_id, signal, remediation="block_promotion")
                apply_incident_metadata(workflow.metadata, incident, decision)
                log_event(
                    "orchestrator.validation_failed",
                    {
                        "workflow_id": wf_id,
                        "error_count": len(errors or []),
                    },
                )
                self.telemetry.record(
                    "validation_error",
                    {"workflow_id": wf_id, "errors": [str(e) for e in errors or []]},
                )
                # MVM decision: raise, but this could be downgraded later.
                raise ValueError(f"Invalid workflow schema for {wf_id}")

            log_event(
                "orchestrator.validation_passed",
                {"workflow_id": wf_id},
            )
            self.telemetry.record(
                "validation_passed",
                {"workflow_id": wf_id},
            )

        # Save to memory and render dashboard
        self.memory.save(workflow.to_dict())
        self.dashboard.render()

        log_event(
            "orchestrator.run.completed",
            {
                "workflow_id": wf_id,
                "phases": phases_to_run,
                "phase_status": dict(phase_status),
            },
        )
        self.telemetry.record(
            "workflow_complete",
            {"workflow_id": wf_id, "phases": phases_to_run},
        )

        logger.info("Workflow orchestration complete for %s", wf_id)
        return workflow
# ---------------------------------------------------------------------- #
