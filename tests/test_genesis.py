"""Tests for the Genesis layer."""

from pathlib import Path
import json
import pytest

from gigagen.core.world_state import WorldState
from gigagen.layers.genesis import run, GenesisError


KILIMA_DIR = Path(__file__).parent.parent / "worlds" / "kilima"


@pytest.fixture
def empty_ws() -> WorldState:
    """Create an empty WorldState for Genesis input."""
    return WorldState(
        world_id="test.world",
        seed=0,
        phase="genesis",
    )


@pytest.fixture
def kilima_config() -> dict:
    """Config pointing to Kilima x.json and y.json."""
    return {
        "x_path": str(KILIMA_DIR / "x.json"),
        "y_path": str(KILIMA_DIR / "y.json"),
    }


class TestGenesisLoadsKilima:
    """Test Genesis with real Kilima data."""

    def test_loads_without_error(self, empty_ws: WorldState, kilima_config: dict) -> None:
        ws = run(empty_ws, kilima_config)
        assert ws is not None

    def test_phase_is_genesis(self, empty_ws: WorldState, kilima_config: dict) -> None:
        ws = run(empty_ws, kilima_config)
        assert ws.phase == "genesis"

    def test_catalogs_populated(self, empty_ws: WorldState, kilima_config: dict) -> None:
        ws = run(empty_ws, kilima_config)
        assert ws.catalogs is not None

    def test_has_12_notes(self, empty_ws: WorldState, kilima_config: dict) -> None:
        ws = run(empty_ws, kilima_config)
        assert len(ws.catalogs.notes) == 12

    def test_has_12_archetypes(self, empty_ws: WorldState, kilima_config: dict) -> None:
        ws = run(empty_ws, kilima_config)
        assert len(ws.catalogs.archetypes) == 12

    def test_has_16_elements(self, empty_ws: WorldState, kilima_config: dict) -> None:
        ws = run(empty_ws, kilima_config)
        assert len(ws.catalogs.elements) == 16

    def test_has_modes(self, empty_ws: WorldState, kilima_config: dict) -> None:
        ws = run(empty_ws, kilima_config)
        assert len(ws.catalogs.modes) >= 7  # at least greek modes

    def test_world_location_created(self, empty_ws: WorldState, kilima_config: dict) -> None:
        ws = run(empty_ws, kilima_config)
        assert "loc.world" in ws.entities

    def test_world_location_is_level_world(self, empty_ws: WorldState, kilima_config: dict) -> None:
        ws = run(empty_ws, kilima_config)
        world = ws.entities["loc.world"]
        assert world.zone_level == "world"

    def test_world_location_in_active_list(self, empty_ws: WorldState, kilima_config: dict) -> None:
        ws = run(empty_ws, kilima_config)
        assert "loc.world" in ws.active_location_ids


class TestGenesisValidation:
    """Test Genesis validation rules."""

    @pytest.fixture
    def tmp_config(self, tmp_path: Path) -> dict:
        """Create temp config with paths."""
        return {
            "x_path": str(tmp_path / "x.json"),
            "y_path": str(tmp_path / "y.json"),
        }

    @pytest.fixture
    def valid_x(self) -> dict:
        """Minimal valid x.json."""
        return {
            "archetypes": [{"code": "TST", "name": "Test"}],
            "modes": {
                "test_mode": {"intervals": [2,2,1,2,2,2,1], "family": "greek"}
            },
            "scale_families": ["greek"],
            "entity_types": ["character"],
            "canon_levels": {"fixed": "desc", "seeded": "desc"},
            "element_tiers": {"fundamental": "desc"},
        }

    @pytest.fixture
    def valid_y(self) -> dict:
        """Minimal valid y.json."""
        return {
            "chromatic_notes": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
            "archetypes": {"TST": "C"},
            "elements": [{"id": "test_elem", "name": "Test", "tier": "fundamental", "components": []}],
            "character_tiers": ["S"],
            "item_tiers": ["S"],
            "skill_tiers": ["S"],
        }

    def test_valid_minimal_config(
        self, empty_ws: WorldState, tmp_path: Path, tmp_config: dict, valid_x: dict, valid_y: dict
    ) -> None:
        (tmp_path / "x.json").write_text(json.dumps(valid_x))
        (tmp_path / "y.json").write_text(json.dumps(valid_y))
        ws = run(empty_ws, tmp_config)
        assert ws.phase == "genesis"

    def test_missing_x_file(self, empty_ws: WorldState, tmp_path: Path, tmp_config: dict, valid_y: dict) -> None:
        (tmp_path / "y.json").write_text(json.dumps(valid_y))
        with pytest.raises(GenesisError, match="File not found"):
            run(empty_ws, tmp_config)

    def test_missing_y_file(self, empty_ws: WorldState, tmp_path: Path, tmp_config: dict, valid_x: dict) -> None:
        (tmp_path / "x.json").write_text(json.dumps(valid_x))
        with pytest.raises(GenesisError, match="File not found"):
            run(empty_ws, tmp_config)

    def test_wrong_note_count(
        self, empty_ws: WorldState, tmp_path: Path, tmp_config: dict, valid_x: dict, valid_y: dict
    ) -> None:
        valid_y["chromatic_notes"] = ["C", "D", "E"]  # Only 3 notes
        (tmp_path / "x.json").write_text(json.dumps(valid_x))
        (tmp_path / "y.json").write_text(json.dumps(valid_y))
        with pytest.raises(GenesisError, match="exactly 12 chromatic notes"):
            run(empty_ws, tmp_config)

    def test_mode_intervals_not_12(
        self, empty_ws: WorldState, tmp_path: Path, tmp_config: dict, valid_x: dict, valid_y: dict
    ) -> None:
        valid_x["modes"]["bad_mode"] = {"intervals": [2,2,2], "family": "test"}  # Sum = 6
        (tmp_path / "x.json").write_text(json.dumps(valid_x))
        (tmp_path / "y.json").write_text(json.dumps(valid_y))
        with pytest.raises(GenesisError, match="intervals sum to"):
            run(empty_ws, tmp_config)

    def test_archetype_invalid_note(
        self, empty_ws: WorldState, tmp_path: Path, tmp_config: dict, valid_x: dict, valid_y: dict
    ) -> None:
        valid_y["archetypes"]["TST"] = "X"  # Invalid note
        (tmp_path / "x.json").write_text(json.dumps(valid_x))
        (tmp_path / "y.json").write_text(json.dumps(valid_y))
        with pytest.raises(GenesisError, match="invalid note"):
            run(empty_ws, tmp_config)

    def test_archetype_not_in_x(
        self, empty_ws: WorldState, tmp_path: Path, tmp_config: dict, valid_x: dict, valid_y: dict
    ) -> None:
        valid_y["archetypes"]["XXX"] = "C"  # Not defined in x.json
        (tmp_path / "x.json").write_text(json.dumps(valid_x))
        (tmp_path / "y.json").write_text(json.dumps(valid_y))
        with pytest.raises(GenesisError, match="not defined in x.json"):
            run(empty_ws, tmp_config)

    def test_element_invalid_component(
        self, empty_ws: WorldState, tmp_path: Path, tmp_config: dict, valid_x: dict, valid_y: dict
    ) -> None:
        valid_y["elements"].append({
            "id": "mixed",
            "name": "Mixed",
            "tier": "fundamental",
            "components": ["nonexistent"]
        })
        (tmp_path / "x.json").write_text(json.dumps(valid_x))
        (tmp_path / "y.json").write_text(json.dumps(valid_y))
        with pytest.raises(GenesisError, match="unknown component"):
            run(empty_ws, tmp_config)

    def test_empty_character_tiers(
        self, empty_ws: WorldState, tmp_path: Path, tmp_config: dict, valid_x: dict, valid_y: dict
    ) -> None:
        valid_y["character_tiers"] = []
        (tmp_path / "x.json").write_text(json.dumps(valid_x))
        (tmp_path / "y.json").write_text(json.dumps(valid_y))
        with pytest.raises(GenesisError, match="must be non-empty"):
            run(empty_ws, tmp_config)


class TestGenesisDeterminism:
    """Test that Genesis is deterministic."""

    def test_same_input_same_output(self, empty_ws: WorldState, kilima_config: dict) -> None:
        ws1 = run(empty_ws, kilima_config)
        ws2 = run(empty_ws, kilima_config)
        # Compare serialized forms
        assert ws1.model_dump_json() == ws2.model_dump_json()

    def test_does_not_modify_input(self, empty_ws: WorldState, kilima_config: dict) -> None:
        original_phase = empty_ws.phase
        original_entities = len(empty_ws.entities)
        _ = run(empty_ws, kilima_config)
        # Input should be unchanged
        assert empty_ws.phase == original_phase
        assert len(empty_ws.entities) == original_entities
