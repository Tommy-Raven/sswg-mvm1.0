#!/usr/bin/env python3
"""
ai_recursive/version_diff_engine.py
Grimoire v4.7 — Diff-Based Regeneration System

Compares two versions of a workflow (JSON or re-imported Markdown) and
detects semantic and structural differences. When differences exceed
a configurable threshold, a regeneration cycle can be triggered automatically.
"""

import json
import os
from difflib import unified_diff
from datetime import datetime
from ai_core.orchestrator import Orchestrator
from ai_monitoring.structured_logger import get_logger, log_event


def load_workflow(path: str) -> dict:
    """Safely load a JSON workflow file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Workflow not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def diff_strings(str1: str, str2: str) -> str:
    """Return a unified diff string between two text values."""
    diff = unified_diff(
        str1.splitlines(),
        str2.splitlines(),
        fromfile="original",
        tofile="modified",
        lineterm=""
    )
    return "\n".join(diff)


def compute_diff_summary(wf_old: dict, wf_new: dict) -> dict:
    """Compute a structured summary of differences between two workflows."""
    summary = {
        "changed_fields": [],
        "added_phases": [],
        "removed_phases": [],
        "modified_phases": [],
        "diff_size": 0,
        "regeneration_recommended": False
    }

    # Compare metadata
    for key, value in wf_new.get("metadata", {}).items():
        old_value = wf_old.get("metadata", {}).get(key)
        if old_value != value:
            summary["changed_fields"].append(("metadata", key, old_value, value))

    # Compare phase titles
    old_titles = [p["title"] for p in wf_old.get("phases", [])]
    new_titles = [p["title"] for p in wf_new.get("phases", [])]

    for title in new_titles:
        if title not in old_titles:
            summary["added_phases"].append(title)
    for title in old_titles:
        if title not in new_titles:
            summary["removed_phases"].append(title)

    # Compare internal logic of shared phases
    for phase_new in wf_new.get("phases", []):
        for phase_old in wf_old.get("phases", []):
            if phase_new["title"] == phase_old["title"]:
                old_text = "\n".join(phase_old.get("tasks", []))
                new_text = "\n".join(phase_new.get("tasks", []))
                if old_text != new_text:
                    diff = diff_strings(old_text, new_text)
                    summary["modified_phases"].append({
                        "title": phase_new["title"],
                        "diff": diff
                    })

    # Compute diff size heuristic
    summary["diff_size"] = (
        len(summary["changed_fields"])
        + len(summary["added_phases"])
        + len(summary["removed_phases"])
        + len(summary["modified_phases"])
    )

    # Trigger regeneration threshold
    summary["regeneration_recommended"] = summary["diff_size"] >= 2
    return summary


def regenerate_if_needed(wf_old: dict, wf_new: dict, threshold: int = 2) -> dict:
    """Trigger workflow regeneration if the diff exceeds threshold."""
    logger = get_logger()
    diff_summary = compute_diff_summary(wf_old, wf_new)
    log_event(logger, "diff_analysis", diff_summary)

    if diff_summary["diff_size"] >= threshold:
        log_event(logger, "regeneration_triggered", {"reason": "diff_threshold_exceeded"})
        orch = Orchestrator()
        print(" Significant divergence from threshold detected. Regenerating workflow...")
        regenerated = orch.run(wf_new.get("metadata", {}))
        return regenerated

    print("Changes below threshold — no regen required. Re-configure threshold for finer asdjustments. default = 2 ")
    return wf_new


def compare_workflows(old_path: str, new_path: str, auto_regen: bool = True) -> dict:
    """
    High-level function for diff-based regeneration.
    Compares two JSON workflow files and optionally regenerates.
    """
    wf_old = load_workflow(old_path)
    wf_new = load_workflow(new_path)

    print(f"\n Comparing versions:\n- Old: {old_path}\n- New: {new_path}")
    diff_summary = compute_diff_summary(wf_old, wf_new)

    if auto_regen:
        wf_final = regenerate_if_needed(wf_old, wf_new)
    else:
        wf_final = wf_new

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"./data/workflows/workflow_diff_{timestamp}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(diff_summary, f, indent=2)

    print(f"Diff summary saved to: {output_path}")
    return wf_final


# ---------------------- Example Execution ---------------------- #

if __name__ == "__main__":
    # Example paths (replace with actual workflow files)
    old_file = "./data/workflows/workflow_original.json"
    new_file = "./data/workflows/workflow_modified.json"

    if os.path.exists(old_file) and os.path.exists(new_file):
        compare_workflows(old_file, new_file)
    else:
        print("ERROR: Example workflow files not found.")
