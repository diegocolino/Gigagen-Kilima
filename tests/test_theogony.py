"""Tests for the Theogony layer."""

from pathlib import Path
import json
import pytest

from gigagen.core.entity import Anima, Lineage
from gigagen.core.world_state import WorldState
from gigagen.layers import genesis, theogony
from gigagen.layers.theogony import TheogonyError


KILIMA_DIR = Path(__file__).parent.parent / "worlds" / "kilima"


@pytest.fixture
def genesis_ws() -> WorldState:
    """Create a WorldState that has passed through Genesis."""
    ws = WorldState(
        world_id="test.world",
        seed=0,
        phase="genesis",
    )
    config = {
        "x_path": str(KILIMA_DIR / "x.json"),
        "y_path": str(KILIMA_DIR / "y.json"),
    }
    return genesis.run(ws, config)


@pytest.fixture
def kilima_theogony_config() -> dict:
    """Config for Theogony with Kilima paths."""
    return {
        "lineages_path": str(KILIMA_DIR / "lineages.json"),
        "locations_path": str(KILIMA_DIR / "locations.json"),
    }


class TestTheogonyRequirements:
    """Test Theogony prerequisites."""

    def test_requires_catalogs(self) -> None:
        ws = WorldState(
            world_id="test",
            seed=0,
            phase="genesis",
            catalogs=None,
        )
        with pytest.raises(TheogonyError, match="requires catalogs"):
            theogony.run(ws, {})


class TestTheogonyAnimas:
    """Test Anima instantiation."""

    def test_creates_16_animas(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        ws = theogony.run(genesis_ws, kilima_theogony_config)
        animas = [e for e in ws.entities.values() if isinstance(e, Anima)]
        assert len(animas) == 16

    def test_anima_ids_prefixed(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        ws = theogony.run(genesis_ws, kilima_theogony_config)
        animas = [e for e in ws.entities.values() if isinstance(e, Anima)]
        for anima in animas:
            assert anima.id.startswith("anima.")

    def test_animas_have_element(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        ws = theogony.run(genesis_ws, kilima_theogony_config)
        animas = [e for e in ws.entities.values() if isinstance(e, Anima)]
        for anima in animas:
            assert anima.element is not None

    def test_animas_not_archetypized(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        """Animas should NOT have note or archetype fields."""
        ws = theogony.run(genesis_ws, kilima_theogony_config)
        animas = [e for e in ws.entities.values() if isinstance(e, Anima)]
        for anima in animas:
            # These fields should not exist on Anima
            assert not hasattr(anima, "note") or getattr(anima, "note", None) is None
            assert not hasattr(anima, "archetype") or getattr(anima, "archetype", None) is None

    def test_supreme_elements_have_supreme_visibility(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        ws = theogony.run(genesis_ws, kilima_theogony_config)
        ether_anima = ws.entities.get("anima.eter_natural")
        assert ether_anima is not None
        assert ether_anima.visibility_class == "supreme_only"


class TestTheogonyLineages:
    """Test Lineage instantiation."""

    def test_loads_13_lineages(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        ws = theogony.run(genesis_ws, kilima_theogony_config)
        lineages = [e for e in ws.entities.values() if isinstance(e, Lineage)]
        assert len(lineages) == 13

    def test_lineage_has_element_pool(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        ws = theogony.run(genesis_ws, kilima_theogony_config)
        lineages = [e for e in ws.entities.values() if isinstance(e, Lineage)]
        for lineage in lineages:
            assert isinstance(lineage.element_pool, list)
            # All lineages except Convergence have non-empty element_pool
            if lineage.id != "lineage.convergence":
                assert len(lineage.element_pool) >= 1

    def test_lineage_seeded_fields_are_none(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        """Seeded fields should be None after Theogony — Chronica resolves them."""
        ws = theogony.run(genesis_ws, kilima_theogony_config)
        lineages = [e for e in ws.entities.values() if isinstance(e, Lineage)]
        for lineage in lineages:
            assert lineage.element is None
            assert lineage.founding_era is None
            assert lineage.origin_location_id is None

    def test_lineages_not_archetypized(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        """Lineages should NOT have note or archetype fields (note_ref is informative, not relational)."""
        ws = theogony.run(genesis_ws, kilima_theogony_config)
        lineages = [e for e in ws.entities.values() if isinstance(e, Lineage)]
        for lineage in lineages:
            # Lineage has note_ref (informative) but NOT note (relational)
            assert not hasattr(lineage, "note") or getattr(lineage, "note", None) is None
            assert not hasattr(lineage, "archetype") or getattr(lineage, "archetype", None) is None

    def test_lineage_has_power_and_population(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        """Lineages should have power and population fields."""
        ws = theogony.run(genesis_ws, kilima_theogony_config)
        radbot = ws.entities.get("lineage.radbot")
        assert radbot is not None
        assert radbot.power == 0.25
        assert radbot.population == 0.05

    def test_lineage_has_status(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        """Lineages should have status field."""
        ws = theogony.run(genesis_ws, kilima_theogony_config)
        lineages = [e for e in ws.entities.values() if isinstance(e, Lineage)]
        statuses = {l.status for l in lineages}
        assert "powerful" in statuses
        assert "relevant" in statuses
        assert "endangered" in statuses
        assert "unknown" in statuses

    def test_convergence_lineage_special(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        """Convergence lineage has special null values."""
        ws = theogony.run(genesis_ws, kilima_theogony_config)
        convergence = ws.entities.get("lineage.convergence")
        assert convergence is not None
        assert convergence.character_id is None
        assert convergence.note_ref is None
        assert convergence.power is None
        assert convergence.population is None
        assert convergence.status == "unknown"
        assert convergence.element_pool == []


class TestTheogonyLocations:
    """Test Level 2 location loading."""

    def test_loads_territory_locations(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        ws = theogony.run(genesis_ws, kilima_theogony_config)
        # Should have at least WORLD from Genesis plus any territories
        territory_locs = [
            e for e in ws.entities.values()
            if getattr(e, "entity_type", None) == "location"
            and getattr(e, "zone_level", None) == "territory"
        ]
        # Kilima has at least one territory
        assert len(territory_locs) >= 1

    def test_territory_locations_have_no_tonic(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        """Tonic assignment happens in Chronica, not Theogony."""
        ws = theogony.run(genesis_ws, kilima_theogony_config)
        territory_locs = [
            e for e in ws.entities.values()
            if getattr(e, "entity_type", None) == "location"
            and getattr(e, "zone_level", None) == "territory"
        ]
        for loc in territory_locs:
            assert loc.tonic is None


class TestTheogonyPhase:
    """Test phase advancement."""

    def test_phase_is_theogony(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        ws = theogony.run(genesis_ws, kilima_theogony_config)
        assert ws.phase == "theogony"


class TestTheogonyValidation:
    """Test validation rules."""

    def test_invalid_element_in_pool_fails(self, genesis_ws: WorldState, tmp_path: Path) -> None:
        lineages_data = {
            "lineages": [
                {
                    "id": "lineage.bad",
                    "name": "Bad",
                    "tier": "founder",
                    "element_pool": ["nonexistent_element"],
                    "canon_level": "fixed",
                }
            ]
        }
        lineages_path = tmp_path / "lineages.json"
        lineages_path.write_text(json.dumps(lineages_data))

        config = {"lineages_path": str(lineages_path)}
        with pytest.raises(TheogonyError, match="unknown element"):
            theogony.run(genesis_ws, config)


class TestTheogonyDeterminism:
    """Test determinism."""

    def test_same_input_same_output(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        ws1 = theogony.run(genesis_ws, kilima_theogony_config)
        ws2 = theogony.run(genesis_ws, kilima_theogony_config)
        assert ws1.model_dump_json() == ws2.model_dump_json()

    def test_does_not_modify_input(self, genesis_ws: WorldState, kilima_theogony_config: dict) -> None:
        original_entities = len(genesis_ws.entities)
        _ = theogony.run(genesis_ws, kilima_theogony_config)
        assert len(genesis_ws.entities) == original_entities
