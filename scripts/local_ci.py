#!/usr/bin/env python3
# scripts/local_ci.py
"""
Local CI runner for SSWG-MVM if GitHub Actions is unavailable.

Tasks:
  - tests   : run pytest for core and API
  - sswg-ci : run lint + schema/template regression tests
  - bench   : run recursive benchmark / memory tracker
  - all     : run sswg-ci, tests, and bench in sequence

Usage:
  python scripts/local_ci.py tests
  python scripts/local_ci.py sswg-ci
  python scripts/local_ci.py bench
  python scripts/local_ci.py all
"""

import argparse
import os
import sys
from dataclasses import dataclass
from subprocess import run as subprocess_run
from typing import List, Sequence


@dataclass
class TaskResult:
    name: str
    command: Sequence[str]
    returncode: int


def run_command(name: str, command: Sequence[str]) -> TaskResult:
    """Run a shell command and capture return code. Keeps behavior transparent."""
    print(f"\n=== [{name}] ===")
    print(" ".join(command))
    try:
        proc = subprocess_run(command, check=False)  # nosec B603
        return TaskResult(name=name, command=command, returncode=proc.returncode)
    except FileNotFoundError as exc:
        print(f"[{name}] ERROR: command not found: {command[0]} ({exc})")
        return TaskResult(name=name, command=command, returncode=127)


def task_pytest_core() -> TaskResult:
    """Core tests under ./tests."""
    return run_command(
        "pytest: core tests",
        ["pytest", "-q", "tests", "--disable-warnings", "--maxfail=1", "--tb=short"],
    )


def task_pytest_api() -> List[TaskResult]:
    """API + generator tests, if those directories exist."""
    results: List[TaskResult] = []

    if os.path.isdir("API/tests"):
        results.append(
            run_command(
                "pytest: API tests",
                [
                    "pytest",
                    "-q",
                    "API/tests",
                    "--disable-warnings",
                    "--maxfail=1",
                    "--tb=short",
                ],
            )
        )
    else:
        print("\n[pytest: API tests] Skipped (API/tests not found).")

    if os.path.isdir("generator/tests"):
        results.append(
            run_command(
                "pytest: generator tests",
                [
                    "pytest",
                    "-q",
                    "generator/tests",
                    "--disable-warnings",
                    "--maxfail=1",
                    "--tb=short",
                ],
            )
        )
    else:
        print("\n[pytest: generator tests] Skipped (generator/tests not found).")

    return results


def task_lint_sswg() -> TaskResult:
    """Lint core SSWG modules and API using flake8, if available."""
    # Adjust module list if your tree changes.
    targets = [
        "generator",
        "ai_core",
        "ai_recursive",
        "ai_validation",
        "ai_graph",
        "ai_monitoring",
        "ai_memory",
        "ai_visualization",
        "API",
    ]
    existing_targets = [t for t in targets if os.path.exists(t)]
    if not existing_targets:
        print("\n[flake8] Skipped (no targets found).")
        return TaskResult(name="flake8: SSWG core", command=["flake8"], returncode=0)

    cmd = ["flake8", *existing_targets, "--max-line-length=120", "--statistics"]
    return run_command("flake8: SSWG core", cmd)


def task_regression_tests() -> TaskResult:
    """
    Run general regression tests for validation layer.
    Relies on ai_validation/regression_tests.py being importable as a module.
    """
    return run_command(
        "ai_validation.regression_tests",
        [sys.executable, "-m", "ai_validation.regression_tests"],
    )


def task_template_regression_tests() -> TaskResult:
    """
    Run template regression tests.
    Relies on ai_validation/template_regression_tests.py being importable as a module.
    """
    return run_command(
        "ai_validation.template_regression_tests",
        [sys.executable, "-m", "ai_validation.template_regression_tests"],
    )


def task_root_contract_validation() -> TaskResult:
    """Validate root contracts and casing rules."""
    return run_command(
        "root contract validation",
        [sys.executable, "scripts/validate_root_contracts.py"],
    )


def task_root_casing_lint() -> TaskResult:
    """Lint casing rules for root contracts."""
    return run_command(
        "root contract casing lint",
        [sys.executable, "scripts/lint_casing.py"],
    )


def task_recursive_benchmark() -> TaskResult:
    """
    Run recursive benchmark / memory tracker.
    This uses the reproducible benchmark pipeline script.
    """
    return run_command(
        "scripts.benchmark_pipeline",
        [sys.executable, "-m", "scripts.benchmark_pipeline", "--repeats", "5"],
    )


def run_tests_suite() -> List[TaskResult]:
    """Run all pytest suites (core + API/generator)."""
    results: List[TaskResult] = []
    results.append(task_pytest_core())
    results.extend(task_pytest_api())
    return results


def run_sswg_ci_suite() -> List[TaskResult]:
    """Run SSWG CI-style checks: lint + validation regressions."""
    results: List[TaskResult] = []
    results.append(task_lint_sswg())
    results.append(task_root_contract_validation())
    results.append(task_root_casing_lint())
    results.append(task_regression_tests())
    results.append(task_template_regression_tests())
    return results


def run_bench_suite() -> List[TaskResult]:
    """Run recursive benchmark / memory tracker."""
    return [task_recursive_benchmark()]


def summarize(results: List[TaskResult]) -> int:
    """Print a summary table and return overall exit code."""
    print("\n========================================")
    print(" Local CI Summary")
    print("========================================")

    overall_rc = 0
    for res in results:
        status = "OK" if res.returncode == 0 else f"FAIL ({res.returncode})"
        print(f"- {res.name}: {status}")
        if res.returncode != 0:
            overall_rc = 1

    if overall_rc == 0:
        print("\nAll tasks succeeded ✅")
    else:
        print("\nOne or more tasks failed ❌")

    return overall_rc


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Local CI runner for SSWG-MVM (tests, SSWG CI checks, recursive benchmark)."
    )
    parser.add_argument(
        "task",
        choices=["tests", "sswg-ci", "bench", "all"],
        help="Which suite to run.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)

    all_results: List[TaskResult] = []

    if args.task in ("sswg-ci", "all"):
        all_results.extend(run_sswg_ci_suite())

    if args.task in ("tests", "all"):
        all_results.extend(run_tests_suite())

    if args.task in ("bench", "all"):
        all_results.extend(run_bench_suite())

    return summarize(all_results)


if __name__ == "__main__":
    raise SystemExit(main())
