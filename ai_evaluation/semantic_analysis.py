#!/usr/bin/env python3
"""
ai_evaluation/semantic_analysis.py — Lightweight text/semantic utilities.

Provides `SemanticAnalyzer`, which operates purely on text content extracted
from workflow objects. No external ML dependencies at MVM.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List


class SemanticAnalyzer:
    """
    Simple semantic/text analysis utilities for workflows.

    Methods operate on schema-style workflow dicts:

        {
          "metadata": {...},
          "phases": [...],
          "modules": [...],
          "outputs": [...]
        }
    """

    def extract_text_blocks(self, workflow: Dict[str, Any]) -> List[str]:
        """
        Collect candidate text fields from metadata, phases, modules, outputs.
        """
        blocks: List[str] = []

        meta = workflow.get("metadata", {}) or {}
        for k, v in meta.items():
            if isinstance(v, str):
                blocks.append(v)

        for ph in workflow.get("phases", []) or []:
            if isinstance(ph, dict):
                desc = ph.get("description")
                if isinstance(desc, str):
                    blocks.append(desc)

        for m in workflow.get("modules", []) or []:
            if isinstance(m, dict):
                for key in ("description", "ai_logic", "human_actionable"):
                    v = m.get(key)
                    if isinstance(v, str):
                        blocks.append(v)

        for out in workflow.get("outputs", []) or []:
            if isinstance(out, dict):
                v = out.get("text")
                if isinstance(v, str):
                    blocks.append(v)

        return blocks

    def average_length(self, blocks: Iterable[str]) -> float:
        """
        Average length (in characters) of text blocks.
        """
        blocks_list = [b for b in blocks if b]
        if not blocks_list:
            return 0.0
        total = sum(len(b) for b in blocks_list)
        return total / len(blocks_list)

    def estimate_redundancy(self, blocks: Iterable[str]) -> float:
        """
        Very rough redundancy estimate: ratio of unique sentences to total.

        Returns:
            1.0   → all sentences unique
            0.0   → everything identical
        """
        sentences: List[str] = []
        for b in blocks:
            sentences.extend(self._split_sentences(b))

        if not sentences:
            return 1.0

        normalized = [s.strip().lower() for s in sentences if s.strip()]
        total = len(normalized)
        unique = len(set(normalized))
        if total == 0:
            return 1.0

        return unique / total

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    _sentence_splitter = re.compile(r"[.!?]+")

    def _split_sentences(self, text: str) -> List[str]:
        return [s for s in self._sentence_splitter.split(text) if s.strip()]
