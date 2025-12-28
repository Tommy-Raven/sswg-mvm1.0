#!/usr/bin/env python3
"""Tests for recursion correctness proofs."""

from ai_recursive import RecursionManager
from tests.assertions import require


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

    require(proof.overall_ok is True, "Expected proof to be OK")
    require(proof.steps, "Expected proof steps")
    require(all(step.ok for step in proof.steps), "Expected all proof steps to pass")


def test_recursion_proof_missing_audit_log():
    manager = RecursionManager()
    proof = manager.prove_correctness("missing-root")

    require(proof.overall_ok is False, "Expected proof to fail without audit log")
    require(proof.steps[0].ok is False, "Expected first proof step to fail")
