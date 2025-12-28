"""
test_config.py — SSWG–MVM Config Tests
"""

import json
import os
import pytest
from datetime import datetime
from pathlib import Path


@pytest.fixture(scope="session")
def base_workflow():
    """A minimal MVM-schema-valid workflow."""
    return {
        "workflow_id": "wf_test_001",
        "version": "v.09.mvm.25",
        "metadata": {
            "purpose": "Testing",
            "audience": "Developers",
            "title": "Test_Workflow",
            "created": datetime.utcnow().isoformat() + "Z",
        },
        "phases": [
            {"id": "P1", "title": "Init", "tasks": [{"desc": "Acquire variables"}]},
            {"id": "P2", "title": "Generate", "tasks": [{"desc": "Draft content"}]},
        ],
        "modules": [],
    }


@pytest.fixture(scope="session")
def invalid_workflow():
    """Intentionally invalid for schema rejection tests."""
    return {"metadata": {"purpose": "Missing required fields"}}


@pytest.fixture(scope="function")
def tmp_json(tmp_path):
    """Creates a temp JSON file for read/write tests."""
    fp = tmp_path / "temp.json"
    fp.write_text(json.dumps({"msg": "test"}))
    return fp


@pytest.fixture(scope="session")
def output_dir(tmp_path_factory):
    """Temporary directory for artifact exports."""
    return tmp_path_factory.mktemp("outputs")


@pytest.fixture(scope="session")
def template_dir():
    return Path("data/templates").absolute()


# Tests configuration loading + template resolution.

from data.data_parsing import load_template
from tests.assertions import require


def test_load_template_by_slug(template_dir):
    data = load_template("creative")
    require(isinstance(data, dict), "Expected template to load as dict")
    require("phases" in data, "Expected template to include phases")
