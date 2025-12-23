"""Lightweight wrapper around the llm_adapter package exports."""

from llm_adapter import generate_text
"""
modules/llm_adapter.py — lightweight text generator shim.

This module intentionally keeps generation deterministic for offline demos:
- Accepts a prompt string.
- Returns a short improvement suggestion derived from the prompt.

The goal is to provide a stable hook for RecursionManager without requiring
network calls or external credentials.
"""

from __future__ import annotations

from textwrap import dedent


def generate_text(prompt: str) -> str:
    """
    Produce a deterministic, prompt-aware suggestion string.

    The implementation keeps the demo pipeline self contained while still
    surfacing the prompt context that triggered regeneration.
    """

    cleaned = " ".join(prompt.split())
    return dedent(
        f"""
        Improvement requested based on: {cleaned}\n
        - Clarify ambiguous steps with concrete inputs and outputs.
        - Add explicit owner + success criteria for each phase.
        - Tighten module dependencies and ensure evaluation hooks run.
        """
    ).strip()
