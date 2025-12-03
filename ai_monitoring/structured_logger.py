#!/usr/bin/env python3
"""
ai_monitoring/structured_logger.py

Structured logging for the SSWG / Grimoire system.

Original behavior:
- get_logger() creates console + file logger at ./logs/workflow.log
- log_event(logger, event, data) records structured events

MVM extensions:
- New convenience signature: log_event(event, payload=None)
  which uses a shared module-level logger.
- All new code can simply call: log_event("mvm.process.started", {"workflow_id": "..."}).
- Backwards-compatible with older usage: log_event(logger, "event", {...})
"""

from __future__ import annotations

import datetime
import logging
import os
from typing import Any, Dict, Optional, Union


LOG_PATH = "./logs/workflow.log"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


def get_logger(name: str = "grimoire") -> logging.Logger:
    """Create or return a configured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

        # File handler
        fh = logging.FileHandler(LOG_PATH)
        fh.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )

        logger.addHandler(ch)
        logger.addHandler(fh)
    return logger


# Module-level default logger for MVM convenience
_default_logger = get_logger("ai_monitoring.structured_logger")


def _format_event(event: str, data: Optional[Dict[str, Any]] = None) -> str:
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    msg = f"[{ts}] EVENT: {event}"
    if data:
        msg += f" | data={data}"
    return msg


def log_event(
    arg1: Union[str, logging.Logger],
    arg2: Optional[Union[str, Dict[str, Any]]] = None,
    arg3: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Unified, backward-compatible structured logging API.

    Supported call styles:

    1) New MVM-style:
        log_event("event_name", {"key": "value"})

    2) Legacy style:
        log = get_logger()
        log_event(log, "event_name", {"key": "value"})

    Args:
        arg1:
            - If str: treated as event name (MVM style).
            - If Logger: treated as logger (legacy style).
        arg2:
            - If arg1 is str: treated as payload dict (optional).
            - If arg1 is Logger: treated as event name (legacy).
        arg3:
            - Only used in legacy style: payload dict.
    """
    # Case 1: MVM style — arg1 is event name, arg2 is payload
    if isinstance(arg1, str):
        event = arg1
        data = arg2 if isinstance(arg2, dict) else None
        logger = _default_logger
    else:
        # Case 2: legacy style — arg1 is logger, arg2 is event, arg3 is payload
        logger = arg1
        event = arg2 if isinstance(arg2, str) else "<unknown_event>"
        data = arg3 if isinstance(arg3, dict) else None

    msg = _format_event(event, data)
    logger.info(msg)


# Example usage
if __name__ == "__main__":
    # Legacy style
    legacy_log = get_logger()
    log_event(legacy_log, "workflow_generated_legacy", {"id": "demo_legacy", "purpose": "testing"})

    # New MVM style
    log_event("workflow_generated_mvm", {"id": "demo_mvm", "purpose": "testing"})
# End of ai_monitoring/structured_logger.py