"""
Tests utility consistency and schema enforcement.
"""

from ai_validation.schema_validator import validate_workflow

from tests.assertions import require


def test_schema_validator_rejects_invalid():
    invalid_wf = {"version": "1.0", "metadata": {}}
    valid, err = validate_workflow(invalid_wf)
    require(not valid, "Expected invalid workflow to fail validation")
    require("required" in err.lower(), "Expected required field error")
