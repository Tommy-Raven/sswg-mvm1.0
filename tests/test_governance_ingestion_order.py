from pathlib import Path
import tomllib

GOVERNANCE_ROOT = Path("directive_core/docs")
CONSTITUTION_PATH = GOVERNANCE_ROOT / "SSWG_CONSTITUTION.toml"

def load_constitution():
    with open(CONSTITUTION_PATH, "rb") as f:
        return tomllib.load(f)

def test_governance_ingestion_order_matches_constitution():
    constitution = load_constitution()

    ingestion = constitution["ingestion_sequence"]["phase"]
    expected_files = [phase["file"] for phase in ingestion]

    # Assert no duplicate phases
    assert len(expected_files) == len(set(expected_files)), (
        "Duplicate governance documents detected in ingestion sequence"
    )

    # Assert all required files exist
    for file in expected_files:
        path = GOVERNANCE_ROOT / file
        assert path.exists(), f"Missing registered governance artifact: {file}"

    # Assert registry-only validation boundary
    registry = constitution["governance_registry"]["artifact"]
    registered_files = {item["path"] for item in registry}

    assert set(expected_files) == registered_files, (
        "Mismatch between ingestion sequence and governance registry"
    )

def test_no_unregistered_toml_in_governance_root():
    constitution = load_constitution()
    registry = constitution["governance_registry"]["artifact"]
    registered_files = {item["path"] for item in registry}

    toml_files = {p.name for p in GOVERNANCE_ROOT.glob("*.toml")}

    unregistered = toml_files - registered_files

    assert not unregistered, (
        f"Unregistered TOML governance artifacts detected: {sorted(unregistered)}"
    )
