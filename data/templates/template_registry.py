#!/usr/bin/env python3
"""
SSWG-MVM Template Registry
Central registry for all workflow templates, providing:
- slug → file resolution
- schema-aware loading
- metadata introspection
- domain classification
- auto-indexing for CLI and orchestrator systems
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except Exception:
    yaml = None

TEMPLATE_DIR = Path("data/templates")


class TemplateRegistry:
    """
    Registry for all SSWG-MVM templates.
    Handles resolving template slugs, reading metadata,
    and enumerating available workflow blueprints.
    """

    def __init__(self, root: Path = TEMPLATE_DIR):
        self.root = root
        self._cache: Dict[str, Dict] = {}

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------
    def list_templates(self) -> List[str]:
        """Return all registered slugs."""
        slugs = []
        for f in self.root.glob("*"):
            if f.suffix in (".json", ".yaml", ".yml"):
                slugs.append(self._slug_from_filename(f))
        return sorted(set(slugs))

    def load(self, slug: str) -> Dict:
        """Load template by slug, from cache if possible."""
        if slug in self._cache:
            return self._cache[slug]

        file_path = self._resolve(slug)
        template = self._load_file(file_path)
        self._cache[slug] = template
        return template

    def metadata(self, slug: str) -> Dict:
        """Extract metadata from a template."""
        tpl = self.load(slug)
        return tpl.get("metadata", {})

    # ------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------
    def _resolve(self, slug: str) -> Path:
        """Find matching template file for a given slug."""
        candidates = [
            self.root / f"{slug}.json",
            self.root / f"{slug}.yaml",
            self.root / f"{slug}.yml",
            self.root / f"{slug}_template.json",
            self.root / f"{slug}_template.yaml",
            self.root / f"{slug}_workflow.json",
        ]
        for c in candidates:
            if c.exists():
                return c
        raise FileNotFoundError(f"No template found for slug '{slug}'")

    def _slug_from_filename(self, path: Path) -> str:
        name = path.stem.replace("_template", "").replace("_workflow", "")
        return name

    def _load_file(self, path: Path) -> Dict:
        if path.suffix == ".json":
            return json.loads(path.read_text(encoding="utf-8"))
        if path.suffix in (".yaml", ".yml"):
            if not yaml:
                raise RuntimeError("yaml module is missing (PyYAML not installed)")
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        raise ValueError(f"Unsupported template type: {path}")


# Singleton-style registry for convenience
registry = TemplateRegistry()

if __name__ == "__main__":
    print("Available Templates:")
    for slug in registry.list_templates():
        print("  -", slug)
