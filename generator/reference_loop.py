"""Reference loop orchestrator for sswg/mvm runs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional

from ai_core.orchestrator import Orchestrator, RunContext
from ai_evaluation.verity_tensor import compute_verity
from ai_memory.benchmark_evolution import BenchmarkEvolution
from ai_memory.entropy_controller import EntropyController, verify_entropy_budget


@dataclass(frozen=True)
class ReferenceLoopResult:
    run_id: str
    run_output: Dict[str, Any]
    entropy_summary: Dict[str, Any]
    benchmark_summary: Dict[str, Any]
    convergence_summary: Dict[str, Any]


def run_reference_loop(
    *,
    workflow_source: Dict[str, Any] | Path,
    run_id: str,
    phases: Optional[Iterable[str]] = None,
    validate_after: bool = True,
    runner: Optional[Callable[..., Any]] = None,
    runner_kwargs: Optional[Dict[str, Any]] = None,
    iterations: int = 1,
    semantic_score: float = 0.0,
    determinism_score: float = 1.0,
    entropy_per_iteration: float = 0.0,
    entropy_budget: float = 1.0,
) -> ReferenceLoopResult:
    """Run a bounded reference loop with orchestration wiring."""
    orchestrator = Orchestrator()
    benchmark = BenchmarkEvolution()
    entropy_controller = EntropyController(max_entropy=entropy_budget)
    run_payload: Dict[str, Any] = {}

    for _ in range(max(1, iterations)):
        context = RunContext(
            workflow_source=workflow_source,
            phases=phases,
            validate_after=validate_after,
            runner=runner,
            runner_kwargs=runner_kwargs or {},
        )
        run_result = orchestrator.run_mvm(context)
        run_payload = {
            "workflow": run_result.workflow_data,
            "phase_status": run_result.phase_status,
        }

        verity_payload = compute_verity(
            semantic_score=semantic_score,
            det_score=determinism_score,
            entropy=entropy_per_iteration,
        )
        benchmark.log_cycle(
            verity=verity_payload["verity"],
            entropy=entropy_per_iteration,
            determinism=determinism_score,
        )
        entropy_controller.log_entropy(entropy_per_iteration)

    entropy_summary = verify_entropy_budget(
        controller=entropy_controller,
        max_entropy=entropy_budget,
    )
    benchmark_summary = benchmark.statistical_summary()
    convergence_summary = benchmark.convergence_summary()

    return ReferenceLoopResult(
        run_id=run_id,
        run_output=run_payload,
        entropy_summary=entropy_summary,
        benchmark_summary=benchmark_summary,
        convergence_summary=convergence_summary,
    )


__all__ = [
    "ReferenceLoopResult",
    "run_reference_loop",
]
