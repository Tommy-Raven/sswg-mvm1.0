#!/usr/bin/env python3
"""
ai_monitoring/structured_logger.py
Structured logging for the Grimoire v4.5 system.

Logs each generation, evaluation, and validation cycle to ./logs/workflow.log
and supports both console and file outputs.
"""

import logging
import os
import datetime
from typing import Dict, Any


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
        fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

        logger.addHandler(ch)
        logger.addHandler(fh)
    return logger


def log_event(logger: logging.Logger, event: str, data: Dict[str, Any] = None):
    """Record a structured event with optional contextual data."""
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    msg = f"[{ts}] EVENT: {event}"
    if data:
        msg += f" | data={data}"
    logger.info(msg)


# Example usage
if __name__ == "__main__":
    log = get_logger()
    log_event(log, "workflow_generated", {"id": "demo_001", "purpose": "testing"})
    
