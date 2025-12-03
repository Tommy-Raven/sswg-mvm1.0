#!/usr/bin/env python3
"""
generator/evaluation.py — Evaluation Engine for SSWG

Handles evaluation of workflow phases in a modular and async-friendly way.

MVM extensions:
- Telemetry events for evaluator registration and execution
- Workflow-aware evaluation (workflow_id + version)
- Supports both sync and async evaluator functions
- Optional result schema validation via ai_validation.schema_validator
- Structured result records with duration and validity flags
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from ai_monitoring.structured_logger import log_event

try:
    from ai_validation.schema_validator import validate_json
except Exception:  # fallback if validation layer isn't wired yet
    def validate_json(obj: Any, schema_name: Optional[str] = None) -> bool:  # type: ignore[no-redef]
        return True


try:
    from meta_knowledge_repo.versioning import get_current_version
except Exception:  # fallback if versioning isn't wired yet
    def get_current_version() -> str:  # type: ignore[no-redef]
        return "0.0.0-MVM"


logger = logging.getLogger("generator.evaluation")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)

EvaluatorFunc = Callable[[Dict[str, Any]], Any]
AsyncEvaluatorFunc = Callable[[Dict[str, Any]], Awaitable[Any]]


class EvaluationEngine:
    """Handles evaluation of workflow phases, modular and async-friendly."""

    def __init__(self, workflow_id: str = "default") -> None:
        self._evaluators: Dict[str, EvaluatorFunc] = {}
        self.workflow_id: str = workflow_id
        self.version: str = get_current_version()
        # Optional: schema name for evaluation result validation
        self.result_schema_name: Optional[str] = "evaluation_result_schema.json"

    # ------------------------------------------------------------------ #
    # Registration
    # ------------------------------------------------------------------ #
    def register_evaluator(
        self,
        phase_name: str,
        func: EvaluatorFunc,
    ) -> None:
        """
        Register an evaluator function for a specific phase.

        Args:
            phase_name: Phase identifier.
            func: Evaluation function (sync or async).
        """
        self._evaluators[phase_name] = func
        logger.info("Registered evaluator for phase: %s", phase_name)

        log_event(
            "evaluation.register",
            {
                "phase": phase_name,
                "workflow_id": self.workflow_id,
                "version": self.version,
                "is_async": asyncio.iscoroutinefunction(func),
            },
        )

    # ------------------------------------------------------------------ #
    # Evaluation helpers
    # ------------------------------------------------------------------ #
    async def _run_evaluator(
        self, evaluator: EvaluatorFunc, context: Dict[str, Any]
    ) -> Any:
        """
        Run a single evaluator, sync or async, and return raw result.
        """
        if asyncio.iscoroutinefunction(evaluator):
            return await evaluator(context)  # type: ignore[arg-type]
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, evaluator, context)

    # ------------------------------------------------------------------ #
    # Public evaluation API
    # ------------------------------------------------------------------ #
    async def evaluate_phase(self, phase_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single phase asynchronously.

        Args:
            phase_name: Phase to evaluate.
            context: Context for evaluation.

        Returns:
            Structured record:
            {
              "phase": phase_name,
              "result": <raw evaluator output>,
              "valid": bool,
              "duration": float,
              "version": str
            }
        """
        evaluator = self._evaluators.get(phase_name)
        if not evaluator:
            logger.warning("No evaluator registered for phase: %s", phase_name)
            log_event(
                "evaluation.missing_evaluator",
                {
                    "phase": phase_name,
                    "workflow_id": self.workflow_id,
                },
            )
            return {
                "phase": phase_name,
                "result": None,
                "valid": False,
                "duration": 0.0,
                "version": self.version,
            }

        log_event(
            "evaluation.phase.started",
            {
                "phase": phase_name,
                "workflow_id": self.workflow_id,
            },
        )

        loop = asyncio.get_running_loop()
        start = loop.time()

        try:
            raw_result = await _safe_run_evaluator(self._run_evaluator, evaluator, context)
        except Exception as e:  # extremely defensive; _safe_run_evaluator already logs
            logger.error("Unexpected error in evaluate_phase(%s): %s", phase_name, e)
            raw_result = None

        duration = loop.time() - start
        valid = validate_json(raw_result, self.result_schema_name)

        log_event(
            "evaluation.phase.completed",
            {
                "phase": phase_name,
                "workflow_id": self.workflow_id,
                "duration": duration,
                "valid": valid,
            },
        )

        return {
            "phase": phase_name,
            "result": raw_result,
            "valid": valid,
            "duration": duration,
            "version": self.version,
        }

    async def evaluate_all(
        self,
        context: Dict[str, Any],
        phases: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Evaluate all registered phases or a subset asynchronously.

        Args:
            context: Workflow context.
            phases: Subset of phases to evaluate. Evaluates all if None.

        Returns:
            Mapping:
              phase_name -> structured evaluation record (see evaluate_phase).
        """
        phases_to_eval = phases or list(self._evaluators.keys())
        results: Dict[str, Dict[str, Any]] = {}

        log_event(
            "evaluation.all.started",
            {
                "workflow_id": self.workflow_id,
                "phase_count": len(phases_to_eval),
            },
        )

        for phase in phases_to_eval:
            results[phase] = await self.evaluate_phase(phase, context)

        log_event(
            "evaluation.all.completed",
            {
                "workflow_id": self.workflow_id,
                "completed_phases": len(results),
            },
        )

        return results


# ---------------------------------------------------------------------- #
# Internal helper for ultra-safe evaluator execution
# ---------------------------------------------------------------------- #
async def _safe_run_evaluator(
    runner: Callable[[EvaluatorFunc, Dict[str, Any]], Awaitable[Any]],
    evaluator: EvaluatorFunc,
    context: Dict[str, Any],
) -> Any:
    """
    Wrap evaluator execution in a try/except, emitting telemetry on errors.
    """
    try:
        return await runner(evaluator, context)
    except Exception as e:
        logger.error("Evaluator error: %s", e)
        log_event(
            "evaluation.evaluator.error",
            {
                "error": str(e),
                "context_keys": list(context.keys()),
            },
        )
        return None
# ----------------------------------------------------------------------