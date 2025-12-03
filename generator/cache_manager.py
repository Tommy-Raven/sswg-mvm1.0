#!/usr/bin/env python3
"""
generator/cache_manager.py — Async-aware Cache Manager for SSWG

Modernized, type-checked, and asyncio compatible.

MVM integrations:
- Telemetry for cache I/O operations
- Version-aware metadata tagging (optional)
- Workflow session binding
- Graceful fallback for corrupted cache reads
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Optional

from ai_monitoring.structured_logger import log_event

try:
    from meta_knowledge_repo.versioning import get_current_version
except Exception:  # fallback if versioning layer isn't wired yet
    def get_current_version() -> str:
        return "0.0.0-MVM"


class CacheManager:
    """Async-aware file cache manager for storing and retrieving workflow artifacts."""

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        workflow_id: str = "default",
    ) -> None:
        """
        Args:
            storage_path: Path to the cache file. If None, caching is disabled.
            workflow_id: Unique identifier for the workflow session.
        """
        self.storage_path = storage_path
        self.workflow_id = workflow_id
        self.version = get_current_version()

        log_event(
            "cache.init",
            {
                "workflow_id": workflow_id,
                "storage_path": str(storage_path) if storage_path else None,
            },
        )

        if self.storage_path is not None:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    async def save(self, data: str) -> None:
        """
        Save data to the cache asynchronously.

        Args:
            data: Serialized data to write.
        """
        if self.storage_path is None:
            return

        log_event(
            "cache.save.started",
            {
                "workflow_id": self.workflow_id,
                "version": self.version,
                "size": len(data),
            },
        )

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.storage_path.write_text, data)

        log_event(
            "cache.save.completed",
            {
                "workflow_id": self.workflow_id,
            },
        )

    async def load(self) -> Optional[str]:
        """
        Load data from the cache asynchronously.

        Returns:
            Cached content, or None if cache file does not exist or failed to read.
        """
        if self.storage_path is None or not self.storage_path.exists():
            return None

        log_event(
            "cache.load.started",
            {
                "workflow_id": self.workflow_id,
                "version": self.version,
            },
        )

        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(None, self.storage_path.read_text)
            log_event(
                "cache.load.completed",
                {
                    "workflow_id": self.workflow_id,
                    "size": len(result),
                },
            )
            return result
        except Exception as e:
            log_event(
                "cache.load.error",
                {
                    "workflow_id": self.workflow_id,
                    "error": str(e),
                },
            )
            return None

    async def clear(self) -> None:
        """
        Clear the cache asynchronously.
        """
        if self.storage_path is None or not self.storage_path.exists():
            return

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.storage_path.unlink)

        log_event(
            "cache.clear.completed",
            {
                "workflow_id": self.workflow_id,
            },
        )
# End of generator/cache_manager.py