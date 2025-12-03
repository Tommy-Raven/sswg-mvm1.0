#!/usr/bin/env python3
"""
generator/async_executor.py
Asynchronous Task Executor for SSWG MVM.

Provides helpers for running synchronous and asynchronous functions concurrently,
with structured telemetry via ai_monitoring.structured_logger.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, Coroutine, Iterable, List, Union

from ai_monitoring.structured_logger import log_event

# ─── Logger Setup ──────────────────────────────────────────────
logger = logging.getLogger("generator.async_executor")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)

# ─── Types ────────────────────────────────────────────────────
AsyncTaskType = Union[Callable[..., Awaitable[Any]], Coroutine[Any, Any, Any]]


# ─── Internal Helpers ─────────────────────────────────────────
async def _normalize_task(task: AsyncTaskType, *args, **kwargs) -> Any:
    """
    Normalize invocation of an async-capable task.

    - If task is a callable, call it with *args, **kwargs and await the result.
    - If task is already a coroutine object, just await it.
    """
    if callable(task):
        return await task(*args, **kwargs)
    return await task


# ─── Core Functions ───────────────────────────────────────────
async def run_task(task: AsyncTaskType, *args, **kwargs) -> Any:
    """
    Run a single asynchronous task (function or coroutine object) with logging and telemetry.
    """
    task_name = getattr(task, "__name__", repr(task))

    log_event("async_task.started", {"task": task_name})
    try:
        result = await _normalize_task(task, *args, **kwargs)
        log_event("async_task.completed", {"task": task_name})
        return result
    except Exception as e:
        logger.error("Task %s failed: %s", task_name, e)
        log_event("async_task.error", {"task": task_name, "error": str(e)})
        return None


async def run_tasks_concurrently(
    tasks: Iterable[AsyncTaskType], *args, **kwargs
) -> List[Any]:
    """
    Run multiple async tasks concurrently.

    Args:
        tasks: Iterable of async callables or coroutine objects.
        *args, **kwargs: Passed through to each callable task.
    """
    # Materialize tasks to avoid double iteration issues
    tasks_list = list(tasks)

    log_event(
        "async_batch.started",
        {"task_count": len(tasks_list), "args_len": len(args), "kwargs_keys": list(kwargs.keys())},
    )

    coros: List[Coroutine[Any, Any, Any]] = []
    for t in tasks_list:
        if callable(t):
            coros.append(t(*args, **kwargs))
        else:
            coros.append(t)

    results = await asyncio.gather(*coros, return_exceptions=True)

    for i, r in enumerate(results):
        if isinstance(r, Exception):
            logger.error("Task #%d failed during concurrent execution: %s", i, r)
            log_event(
                "async_batch.task_error",
                {"index": i, "error": str(r)},
            )
            results[i] = None

    log_event("async_batch.completed", {"task_count": len(results)})
    return results


# ─── Synchronous Helpers ──────────────────────────────────────
def run_sync(task: AsyncTaskType, *args, **kwargs) -> Any:
    """
    Synchronous wrapper around run_task for convenience.
    """
    return asyncio.run(run_task(task, *args, **kwargs))


def run_all_sync(tasks: Iterable[AsyncTaskType], *args, **kwargs) -> List[Any]:
    """
    Synchronous wrapper around run_tasks_concurrently for convenience.
    """
    return asyncio.run(run_tasks_concurrently(tasks, *args, **kwargs))


# ─── MVM Extensions ───────────────────────────────────────────
def create_async_task(task: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """
    Factory wrapper used by workflow builder to standardize async execution.

    This is a light abstraction hook for future orchestration layers.
    """
    async def wrapped(*args, **kwargs):
        return await task(*args, **kwargs)

    return wrapped
# End of generator/async_executor.py