import pytest

from scripts.validate_governance_ingestion import validate_governance_documents
from scripts.validate_semantic_ambiguity import SemanticAmbiguityError


def test_appendix_a_is_loaded_and_enforced(tmp_path):
    """
    Appendix A MUST be present and MUST be enforced.
    """

    # Arrange: create a minimal governance doc with ambiguity
    bad_doc = tmp_path / "BAD_GOVERNANCE.toml"
    bad_doc.write_text("""
[anchor]
anchor_id = "bad_doc"
anchor_model = "sswg+mvm+version"
anchor_version = "1.0.0"
scope = "directive_core/docs"
status = "invariant"

[policy]
description = "This may be interpreted as acceptable under special circumstances."
""")

    # Act / Assert
    with pytest.raises(SemanticAmbiguityError) as excinfo:
        validate_governance_documents(
            additional_docs=[bad_doc]
        )

    # Assert: fail-closed, generic message
    msg = str(excinfo.value)
    assert "Semantic Ambiguity" in msg

    # Assert: no leakage of rule IDs or regex names
    forbidden_leaks = [
        "semantic_confusion_tactics",
        "interpretive_permission_language",
        "regex",
        "pattern",
        "trigger"
    ]

    for leak in forbidden_leaks:
        assert leak not in msg.lower()


def test_appendix_a_blocks_yaml_authority(tmp_path):
    """
    YAML authoritative governance SHALL be rejected.
    """

    yaml_doc = tmp_path / "BAD_GOVERNANCE.yaml"
    yaml_doc.write_text("""
anchor:
  anchor_id: bad_yaml
  anchor_model: sswg+mvm+version
  anchor_version: "1.0.0"
  scope: directive_core/docs
  status: invariant
""")

    with pytest.raises(Exception) as excinfo:
        validate_governance_documents(
            additional_docs=[yaml_doc]
        )

    assert "Invalid Canonical Header" in str(excinfo.value)


def test_appendix_a_requires_ingestion_order():
    """
    Governance ingestion MUST respect Appendix A ordering.
    """

    result = validate_governance_documents()

    assert result.ingestion_order_enforced is True
    assert result.appendix_A_enforced is True
  
