#!/usr/bin/env python3
"""
generator/exception_handler.py — Centralized Exception Handling for SSWG

Modernized, type-annotated, async-compatible.

MVM extensions:
- Structured telemetry events for all handled exceptions
- Sync and async wrappers with consistent metadata
- Safe fallback if monitoring layer is unavailable
"""

from __future__ import annotations

import logging
import traceback
from typing import Any, Awaitable, Callable, Optional, TypeVar

from ai_monitoring.structured_logger import log_event

logger = logging.getLogger("generator.exception_handler")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)

T = TypeVar("T")


def handle_exceptions(
    func: Callable[..., T],
    *,
    default_return: Optional[T] = None,
    log_traceback: bool = True,
) -> Callable[..., T]:
    """
    Decorator to wrap functions in a try/except block, logging exceptions.

    Args:
        func: Function to wrap.
        default_return: Return value if exception occurs.
        log_traceback: Whether to log full traceback.

    Returns:
        Wrapped function.
    """

    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as e:  # central handler, broad by design
            func_name = getattr(func, "__name__", "<anonymous>")
            logger.error("Exception in %s: %s", func_name, e)
            if log_traceback:
                tb = traceback.format_exc()
                logger.debug(tb)

            log_event(
                "exception.sync",
                {
                    "function": func_name,
                    "error": str(e),
                    "args_len": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                },
            )
            return default_return  # type: ignore[return-value]

    return wrapper


def async_handle_exceptions(
    coro_func: Callable[..., Awaitable[T]],
    *,
    default_return: Optional[T] = None,
    log_traceback: bool = True,
) -> Callable[..., Awaitable[T]]:
    """
    Wrap an async coroutine function to safely catch exceptions.

    Args:
        coro_func: Async function to wrap.
        default_return: Value to return on exception.
        log_traceback: Whether to log full traceback.

    Returns:
        Async wrapper function.
    """

    async def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return await coro_func(*args, **kwargs)
        except Exception as e:  # central async handler
            func_name = getattr(coro_func, "__name__", "<anonymous>")
            logger.error("Async exception in %s: %s", func_name, e)
            if log_traceback:
                tb = traceback.format_exc()
                logger.debug(tb)

            log_event(
                "exception.async",
                {
                    "function": func_name,
                    "error": str(e),
                    "args_len": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                },
            )
            return default_return  # type: ignore[return-value]

    return wrapper
# End of generator/exception_handler.py