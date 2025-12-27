#!/usr/bin/env python3
"""Tests for recursion correctness proofs."""

from ai_recursive import RecursionManager


def test_recursion_proof_success():
    manager = RecursionManager(max_depth=3, max_children=5, cost_budget=10.0)
    manager.prepare_call(
        root_id="root",
        parent_id=None,
        depth=1,
        estimated_cost=2.0,
        termination_condition="depth",
    )
    manager.prepare_call(
        root_id="root",
        parent_id="root",
        depth=2,
        estimated_cost=1.0,
        termination_condition="budget",
    )

    proof = manager.prove_correctness("root")

    assert proof.overall_ok is True
    assert proof.steps
    assert all(step.ok for step in proof.steps)


def test_recursion_proof_missing_audit_log():
    manager = RecursionManager()
    proof = manager.prove_correctness("missing-root")

    assert proof.overall_ok is False
    assert proof.steps[0].ok is False
