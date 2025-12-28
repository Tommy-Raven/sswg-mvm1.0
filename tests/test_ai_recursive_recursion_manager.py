#!/usr/bin/env python3
"""Unit tests for ai_recursive.recursion_manager."""

from ai_recursive import RecursionManager, RecursionSnapshot
from ai_recursive import (
    RecursionBudgetError,
    RecursionCheckpointError,
    RecursionLimitError,
    RecursionTerminationError,
)
from tests.assertions import require


def test_depth_and_child_limits():
    manager = RecursionManager(max_depth=2, max_children=2, cost_budget=10.0)

    manager.prepare_call(
        root_id="root",
        parent_id=None,
        depth=1,
        estimated_cost=1.0,
        termination_condition="depth",
    )
    manager.prepare_call(
        root_id="root",
        parent_id="root",
        depth=2,
        estimated_cost=1.0,
        termination_condition="depth",
    )

    try:
        manager.prepare_call(
            root_id="root",
            parent_id="root",
            depth=3,
            estimated_cost=1.0,
            termination_condition="depth",
        )
    except RecursionLimitError:
        pass
    else:  # pragma: no cover - safety net
        raise AssertionError("Depth limit should raise RecursionLimitError")

    try:
        manager.prepare_call(
            root_id="root",
            parent_id="root",
            depth=1,
            estimated_cost=1.0,
            termination_condition="depth",
        )
    except RecursionLimitError:
        pass
    else:  # pragma: no cover - safety net
        raise AssertionError("Child cap should raise RecursionLimitError")


def test_budget_exhaustion():
    manager = RecursionManager(max_depth=2, max_children=3, cost_budget=2.5)
    manager.prepare_call(
        root_id="root",
        parent_id=None,
        depth=1,
        estimated_cost=1.5,
        termination_condition="budget",
    )

    try:
        manager.prepare_call(
            root_id="root",
            parent_id="root",
            depth=2,
            estimated_cost=1.1,
            termination_condition="budget",
        )
    except RecursionBudgetError:
        pass
    else:  # pragma: no cover - safety net
        raise AssertionError("Budget exhaustion should raise RecursionBudgetError")


def test_checkpoint_invocation_and_audit_trail():
    calls = []

    def checkpoint(snapshot: RecursionSnapshot) -> bool:
        calls.append(snapshot)
        return True

    manager = RecursionManager(
        max_depth=3,
        max_children=5,
        cost_budget=10.0,
        checkpoint_ratio=0.5,
        checkpoint_handler=checkpoint,
    )

    snapshot = manager.prepare_call(
        root_id="root",
        parent_id=None,
        depth=2,
        estimated_cost=5.0,
        termination_condition="depth",
    )

    require(calls, "Checkpoint handler should have been invoked")
    require(calls[0] == snapshot, "Expected snapshot to be recorded")

    audit_log = manager.get_audit_log("root")
    require(len(audit_log) == 1, "Expected single audit log entry")
    require(
        audit_log[0].budget_remaining == 5.0,
        "Expected budget remaining to be updated",
    )


def test_checkpoint_denial_blocks_recursion():
    def deny(snapshot: RecursionSnapshot) -> bool:
        return False

    manager = RecursionManager(
        max_depth=2,
        max_children=3,
        cost_budget=10.0,
        checkpoint_ratio=0.0,
        checkpoint_handler=deny,
    )

    try:
        manager.prepare_call(
            root_id="root",
            parent_id=None,
            depth=1,
            estimated_cost=1.0,
            termination_condition="checkpoint",
        )
    except RecursionCheckpointError:
        pass
    else:  # pragma: no cover - safety net
        raise AssertionError("Denied checkpoint should raise RecursionCheckpointError")


def test_missing_termination_condition_rejected():
    manager = RecursionManager()
    try:
        manager.prepare_call(
            root_id="root",
            parent_id=None,
            depth=1,
            estimated_cost=0.0,
            termination_condition=None,
        )
    except RecursionTerminationError:
        pass
    else:  # pragma: no cover - safety net
        raise AssertionError("Missing termination condition should be rejected")
