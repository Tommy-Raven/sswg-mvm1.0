#!/usr/bin/env python3
"""
generator/config.py — Configuration Management for SSWG

Async-aware configuration manager for loading and saving workflow settings.

MVM integrations:
- Telemetry hooks for load/save/update
- Workflow-aware metadata (workflow_id)
- Optional JSON schema validation for configs
- Version tagging using meta_knowledge_repo.versioning
- Graceful handling of corrupted JSON
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Optional

from ai_monitoring.structured_logger import log_event

try:
    from ai_validation.schema_validator import validate_json
except Exception:  # fallback if validation layer isn't wired yet
    def validate_json(obj: Any, schema_name: Optional[str] = None) -> bool:  # type: ignore[no-redef]
        return True


try:
    from meta_knowledge_repo.versioning import get_current_version
except Exception:  # fallback if versioning isn't wired yet
    def get_current_version() -> str:  # type: ignore[no-redef]
        return "0.0.0-MVM"


class ConfigManager:
    """Async-aware configuration manager for loading and saving workflow settings."""

    def __init__(
        self,
        config_path: Optional[Path] = None,
        default_config: Optional[Dict[str, Any]] = None,
        workflow_id: str = "default",
        schema_name: Optional[str] = "config_schema.json",
    ) -> None:
        """
        Args:
            config_path: Path to JSON configuration file. If None, config is in-memory only.
            default_config: Default configuration to initialize if file is missing.
            workflow_id: Identifier for the workflow session.
            schema_name: Optional schema to validate the config against.
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = default_config or {}
        self.workflow_id = workflow_id
        self.version = get_current_version()
        self.schema_name = schema_name

        log_event(
            "config.init",
            {
                "workflow_id": self.workflow_id,
                "path": str(self.config_path) if self.config_path else None,
            },
        )

    async def load(self) -> None:
        """Load configuration from JSON file asynchronously."""
        if self.config_path is None or not self.config_path.exists():
            return

        log_event(
            "config.load.started",
            {
                "workflow_id": self.workflow_id,
                "path": str(self.config_path),
            },
        )

        loop = asyncio.get_running_loop()
        try:
            content = await loop.run_in_executor(None, self.config_path.read_text)
            parsed = json.loads(content)

            # Perform schema validation if requested
            if self.schema_name and not validate_json(parsed, self.schema_name):
                log_event(
                    "config.load.validation_failed",
                    {
                        "workflow_id": self.workflow_id,
                        "schema_name": self.schema_name,
                    },
                )
            else:
                self.config = parsed

        except json.JSONDecodeError as e:
            log_event(
                "config.load.error_json",
                {
                    "workflow_id": self.workflow_id,
                    "error": str(e),
                },
            )
        except Exception as e:  # pragma: no cover - defensive
            log_event(
                "config.load.error",
                {
                    "workflow_id": self.workflow_id,
                    "error": str(e),
                },
            )

    async def save(self) -> None:
        """Save current configuration to JSON file asynchronously."""
        if self.config_path is None:
            return

        # Add version + workflow metadata before writing
        self.config["_version"] = self.version
        self.config["_workflow_id"] = self.workflow_id

        log_event(
            "config.save.started",
            {
                "workflow_id": self.workflow_id,
                "path": str(self.config_path),
            },
        )

        loop = asyncio.get_running_loop()
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        await loop.run_in_executor(
            None,
            self.config_path.write_text,
            json.dumps(self.config, indent=2),
        )

        log_event(
            "config.save.completed",
            {
                "workflow_id": self.workflow_id,
            },
        )

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieve a configuration value.

        Args:
            key: Configuration key.
            default: Default value if key is missing.

        Returns:
            Value from config or default.
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key.
            value: Value to store.
        """
        self.config[key] = value

        log_event(
            "config.update",
            {
                "workflow_id": self.workflow_id,
                "key": key,
                "type": str(type(value)),
            },
        )
# End of generator/config.py