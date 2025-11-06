"""
Grimoire v4.8 — Pytest Fixtures
Centralized test data, mock workflows, and config utilities.
"""

import os
import pytest
import json
from datetime import datetime


@pytest.fixture(scope="session")
def base_workflow():
    """Returns a minimal valid workflow dictionary."""
    return {
        "workflow_id": "wf_test_001",
        "version": "1.0",
        "metadata": {
            "purpose": "Testing",
            "audience": "Developers",
            "created": datetime.now().isoformat(),
        },
        "phases": [
            {"id": "phase_1", "title": "Initialization", "tasks": ["Set objective", "Acquire variables"]},
            {"id": "phase_2", "title": "Generation", "tasks": ["Generate draft", "Refine structure"]},
        ],
        "dependency_graph": {
            "nodes": ["Initialization", "Generation"],
            "edges": [["Initialization", "Generation"]],
        },
    }


@pytest.fixture(scope="session")
def invalid_workflow():
    """Returns an intentionally invalid workflow to test schema validation."""
    return {"metadata": {"purpose": "Missing required fields"}}


@pytest.fixture(scope="session")
def temp_json(tmp_path):
    """Creates and returns a temporary JSON file path."""
    file_path = tmp_path / "temp.json"
    with open(file_path, "w") as f:
        json.dump({"msg": "test"}, f)
    return file_path


@pytest.fixture(scope="session")
def output_dir(tmp_path):
    """Provides a temporary output directory for exports."""
    os.makedirs(tmp_path, exist_ok=True)
    return tmp_path


@pytest.fixture(scope="session")
def schema_dir():
    """Returns the path to the schemas directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../schemas"))
