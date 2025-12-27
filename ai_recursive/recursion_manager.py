#!/usr/bin/env python3
"""
ai_recursive/recursion_manager.py — Guardrails for recursive refinement.

This module enforces hard safety constraints for recursive workflows:

- Depth ceilings and child-count caps
- Cost/complexity budgets with decay penalties
- External checkpoints when thresholds are approached
- Mandatory termination conditions per call
- Immutable audit trails for post-mortems

The implementation is intentionally lightweight for MVM while still
providing strict runtime checks and structured logging hooks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Optional


class RecursionLimitError(RuntimeError):
    """Raised when depth/child ceilings are exceeded."""


class RecursionBudgetError(RuntimeError):
    """Raised when a cost or complexity budget is exhausted."""


class RecursionCheckpointError(RuntimeError):
    """Raised when an external checkpoint denies further recursion."""


class RecursionTerminationError(RuntimeError):
    """Raised when a recursive call lacks a termination condition."""


@dataclass(frozen=True)
class ProofStep:
    statement: str
    ok: bool
    evidence: str


@dataclass(frozen=True)
class RecursionProof:
    root_id: str
    overall_ok: bool
    steps: List[ProofStep]


@dataclass(frozen=True)
class RecursionSnapshot:
    root_id: str
    parent_id: Optional[str]
    depth: int
    children_generated: int
    cost_spent: float
    budget_remaining: float
    termination_condition: str
    timestamp: str


@dataclass
class _RecursionState:
    children_count: int = 0
    cost_spent: float = 0.0
    audit_log: List[RecursionSnapshot] = field(default_factory=list)


class RecursionManager:
    """Manage recursion guardrails for workflow refinement."""

    def __init__(
        self,
        *,
        max_depth: int = 3,
        max_children: int = 12,
        cost_budget: float = 1_000.0,
        checkpoint_ratio: float = 0.8,
        checkpoint_handler: Optional[Callable[[RecursionSnapshot], bool]] = None,
    ) -> None:
        if max_depth < 1:
            raise ValueError("max_depth must be >= 1")
        if max_children < 1:
            raise ValueError("max_children must be >= 1")
        if cost_budget <= 0:
            raise ValueError("cost_budget must be positive")
        if not (0.0 <= checkpoint_ratio <= 1.0):
            raise ValueError("checkpoint_ratio must be between 0.0 and 1.0")

        self.max_depth = max_depth
        self.max_children = max_children
        self.cost_budget = float(cost_budget)
        self.checkpoint_ratio = checkpoint_ratio
        self.checkpoint_handler = checkpoint_handler

        self._state: Dict[str, _RecursionState] = {}

    def start_root(self, root_id: str) -> None:
        """Initialize tracking for a new recursion root."""
        self._state[root_id] = _RecursionState()

    def prepare_call(
        self,
        *,
        root_id: str,
        parent_id: Optional[str],
        depth: int,
        estimated_cost: float,
        termination_condition: Optional[str],
    ) -> RecursionSnapshot:
        """
        Validate and register an impending recursive call.

        Raises:
            RecursionLimitError: depth or child ceilings exceeded.
            RecursionBudgetError: budget would be exceeded by the call.
            RecursionCheckpointError: checkpoint handler denied continuation.
            RecursionTerminationError: no termination condition specified.
        """

        if not termination_condition:
            raise RecursionTerminationError(
                "Recursive calls must declare a termination condition."
            )

        state = self._state.setdefault(root_id, _RecursionState())
        self._enforce_depth(depth)
        self._enforce_child_limit(state)
        self._apply_cost(state, estimated_cost)

        snapshot = self._record_snapshot(
            root_id=root_id,
            parent_id=parent_id,
            depth=depth,
            termination_condition=termination_condition,
            state=state,
        )
        self._checkpoint_if_needed(snapshot)

        return snapshot

    def _enforce_depth(self, depth: int) -> None:
        if depth > self.max_depth:
            raise RecursionLimitError(
                f"Recursion depth {depth} exceeds max_depth {self.max_depth}."
            )

    def _enforce_child_limit(self, state: _RecursionState) -> None:
        if state.children_count >= self.max_children:
            raise RecursionLimitError(
                f"Child limit reached: {state.children_count} >= {self.max_children}."
            )
        state.children_count += 1

    def _apply_cost(self, state: _RecursionState, estimated_cost: float) -> None:
        estimated_cost = max(0.0, estimated_cost)
        projected = state.cost_spent + estimated_cost
        if projected > self.cost_budget:
            raise RecursionBudgetError(
                f"Cost budget exceeded: {projected:.2f} > {self.cost_budget:.2f}."
            )
        state.cost_spent = projected

    def _record_snapshot(
        self,
        *,
        root_id: str,
        parent_id: Optional[str],
        depth: int,
        termination_condition: str,
        state: _RecursionState,
    ) -> RecursionSnapshot:
        snapshot = RecursionSnapshot(
            root_id=root_id,
            parent_id=parent_id,
            depth=depth,
            children_generated=state.children_count,
            cost_spent=state.cost_spent,
            budget_remaining=max(0.0, self.cost_budget - state.cost_spent),
            termination_condition=termination_condition,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
        state.audit_log.append(snapshot)
        return snapshot

    def _checkpoint_if_needed(self, snapshot: RecursionSnapshot) -> None:
        if not self.checkpoint_handler:
            return

        depth_ratio = snapshot.depth / float(self.max_depth)
        cost_ratio = (
            snapshot.cost_spent / self.cost_budget if self.cost_budget else 0.0
        )
        if depth_ratio >= self.checkpoint_ratio or cost_ratio >= self.checkpoint_ratio:
            allowed = self.checkpoint_handler(snapshot)
            if allowed is False:
                raise RecursionCheckpointError(
                    "External checkpoint denied further recursion."
                )

    def get_audit_log(self, root_id: str) -> List[RecursionSnapshot]:
        """Return the audit trail for a recursion root."""
        return list(self._state.get(root_id, _RecursionState()).audit_log)

    def prove_correctness(self, root_id: str) -> RecursionProof:
        """
        Calculate a formal proof of correctness for recorded recursion data.

        The proof verifies invariants derived from the guardrails:
        - Depth never exceeds max_depth.
        - Child counts are strictly sequential and capped at max_children.
        - Cost spent is monotonic and within cost_budget.
        - Termination conditions are present for every call.
        - Budget remaining matches cost_spent.
        """
        state = self._state.get(root_id)
        if not state or not state.audit_log:
            steps = [
                ProofStep(
                    statement="Audit log exists for root_id",
                    ok=False,
                    evidence=f"No audit log recorded for root_id={root_id}.",
                )
            ]
            return RecursionProof(root_id=root_id, overall_ok=False, steps=steps)

        snapshots = state.audit_log
        max_depth_seen = max(snapshot.depth for snapshot in snapshots)
        min_depth_seen = min(snapshot.depth for snapshot in snapshots)
        depth_ok = all(
            0 <= snapshot.depth <= self.max_depth for snapshot in snapshots
        )
        depth_step = ProofStep(
            statement="Depth is bounded by max_depth",
            ok=depth_ok,
            evidence=(
                f"min_depth={min_depth_seen}, max_depth_seen={max_depth_seen}, "
                f"max_depth={self.max_depth}."
            ),
        )

        expected_children = list(range(1, len(snapshots) + 1))
        observed_children = [snapshot.children_generated for snapshot in snapshots]
        child_sequence_ok = observed_children == expected_children
        child_limit_ok = observed_children[-1] <= self.max_children
        child_step = ProofStep(
            statement="Children are sequential and within max_children",
            ok=child_sequence_ok and child_limit_ok,
            evidence=(
                f"observed_children={observed_children}, "
                f"max_children={self.max_children}."
            ),
        )

        costs = [snapshot.cost_spent for snapshot in snapshots]
        cost_monotonic = all(
            later >= earlier for earlier, later in zip(costs, costs[1:])
        )
        cost_budget_ok = costs[-1] <= self.cost_budget
        cost_step = ProofStep(
            statement="Cost is monotonic and within cost_budget",
            ok=cost_monotonic and cost_budget_ok,
            evidence=(
                f"costs={costs}, cost_budget={self.cost_budget:.2f}."
            ),
        )

        termination_ok = all(
            snapshot.termination_condition.strip() for snapshot in snapshots
        )
        termination_step = ProofStep(
            statement="Termination condition exists for each call",
            ok=termination_ok,
            evidence=(
                f"termination_conditions="
                f"{[snapshot.termination_condition for snapshot in snapshots]}."
            ),
        )

        budget_remaining_ok = all(
            abs(
                snapshot.budget_remaining
                - max(0.0, self.cost_budget - snapshot.cost_spent)
            )
            < 1e-9
            for snapshot in snapshots
        )
        budget_step = ProofStep(
            statement="Budget remaining matches cost_spent",
            ok=budget_remaining_ok,
            evidence=(
                "budget_remaining="
                f"{[snapshot.budget_remaining for snapshot in snapshots]}."
            ),
        )

        steps = [
            depth_step,
            child_step,
            cost_step,
            termination_step,
            budget_step,
        ]
        overall_ok = all(step.ok for step in steps)
        return RecursionProof(root_id=root_id, overall_ok=overall_ok, steps=steps)
