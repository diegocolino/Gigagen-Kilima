"""Tests for the Chronica layer."""

from pathlib import Path
import pytest

from gigagen.core.entity import Lineage
from gigagen.core.world_state import WorldState
from gigagen.layers import genesis, theogony, chronica
from gigagen.layers.chronica import ChronicaError, SeedEngine


KILIMA_DIR = Path(__file__).parent.parent / "worlds" / "kilima"


@pytest.fixture
def theogony_ws() -> WorldState:
    """Create a WorldState that has passed through Genesis and Theogony."""
    ws = WorldState(
        world_id="test.world",
        seed=0,
        phase="genesis",
    )
    genesis_config = {
        "x_path": str(KILIMA_DIR / "x.json"),
        "y_path": str(KILIMA_DIR / "y.json"),
    }
    ws = genesis.run(ws, genesis_config)

    theogony_config = {
        "lineages_path": str(KILIMA_DIR / "lineages.json"),
        "locations_path": str(KILIMA_DIR / "locations.json"),
    }
    return theogony.run(ws, theogony_config)


class TestSeedEngine:
    """Test the SeedEngine RNG system."""

    def test_same_seed_same_namespace_same_result(self) -> None:
        """Same seed + namespace produces same RNG sequence."""
        engine1 = SeedEngine(42)
        engine2 = SeedEngine(42)

        rng1 = engine1.rng("elements")
        rng2 = engine2.rng("elements")

        # Generate several values and compare
        values1 = [rng1.random() for _ in range(10)]
        values2 = [rng2.random() for _ in range(10)]

        assert values1 == values2

    def test_different_seeds_different_results(self) -> None:
        """Different seeds produce different RNG sequences."""
        engine1 = SeedEngine(42)
        engine2 = SeedEngine(43)

        rng1 = engine1.rng("elements")
        rng2 = engine2.rng("elements")

        values1 = [rng1.random() for _ in range(10)]
        values2 = [rng2.random() for _ in range(10)]

        assert values1 != values2

    def test_different_namespaces_independent(self) -> None:
        """Different namespaces produce independent RNG streams."""
        engine = SeedEngine(42)

        rng_elements = engine.rng("elements")
        rng_founders = engine.rng("founders")

        # Draw from elements
        elements_val = rng_elements.random()

        # Create fresh engine, draw from founders first
        engine2 = SeedEngine(42)
        rng_founders2 = engine2.rng("founders")
        _ = rng_founders2.random()  # consume one value

        # Now get elements — should still match first engine
        rng_elements2 = engine2.rng("elements")
        elements_val2 = rng_elements2.random()

        assert elements_val == elements_val2

    def test_namespace_caching(self) -> None:
        """Same namespace returns same RNG instance."""
        engine = SeedEngine(42)

        rng1 = engine.rng("test")
        rng2 = engine.rng("test")

        assert rng1 is rng2

    def test_seed_property(self) -> None:
        """Engine exposes its seed."""
        engine = SeedEngine(123)
        assert engine.seed == 123


class TestChronicaRequirements:
    """Test Chronica prerequisites."""

    def test_requires_catalogs(self) -> None:
        ws = WorldState(
            world_id="test",
            seed=0,
            phase="theogony",
            catalogs=None,
        )
        with pytest.raises(ChronicaError, match="requires catalogs"):
            chronica.run(ws, {})


class TestChronicaLineageResolution:
    """Test lineage element resolution."""

    def test_lineages_have_element_after_chronica(self, theogony_ws: WorldState) -> None:
        ws = chronica.run(theogony_ws, {}, seed=42)
        lineages = [e for e in ws.entities.values() if isinstance(e, Lineage)]

        for lineage in lineages:
            # Skip Convergence which has empty element_pool
            if lineage.id == "lineage.convergence":
                assert lineage.element is None
            else:
                assert lineage.element is not None

    def test_element_is_from_pool(self, theogony_ws: WorldState) -> None:
        ws = chronica.run(theogony_ws, {}, seed=42)
        lineages = [e for e in ws.entities.values() if isinstance(e, Lineage)]

        for lineage in lineages:
            if lineage.element_pool:
                assert lineage.element in lineage.element_pool

    def test_same_seed_same_elements(self, theogony_ws: WorldState) -> None:
        ws1 = chronica.run(theogony_ws, {}, seed=42)
        ws2 = chronica.run(theogony_ws, {}, seed=42)

        lineages1 = {l.id: l.element for l in ws1.entities.values() if isinstance(l, Lineage)}
        lineages2 = {l.id: l.element for l in ws2.entities.values() if isinstance(l, Lineage)}

        assert lineages1 == lineages2

    def test_different_seeds_can_produce_different_elements(self, theogony_ws: WorldState) -> None:
        """Different seeds can produce different element assignments.

        Note: With only 4 elements in pool and 12 lineages, there's a small
        chance this could fail randomly. We test many seeds to ensure variety.
        """
        elements_by_seed = {}
        for seed in range(100):
            ws = chronica.run(theogony_ws, {}, seed=seed)
            radbot = ws.entities.get("lineage.radbot")
            if radbot:
                elements_by_seed[seed] = radbot.element

        # Should have at least 2 different elements across 100 seeds
        unique_elements = set(elements_by_seed.values())
        assert len(unique_elements) >= 2


class TestChronicaPhase:
    """Test phase advancement."""

    def test_phase_is_chronica(self, theogony_ws: WorldState) -> None:
        ws = chronica.run(theogony_ws, {}, seed=42)
        assert ws.phase == "chronica"

    def test_seed_stored_in_worldstate(self, theogony_ws: WorldState) -> None:
        ws = chronica.run(theogony_ws, {}, seed=42)
        assert ws.seed == 42


class TestChronicaDeterminism:
    """Test determinism."""

    def test_same_seed_same_output(self, theogony_ws: WorldState) -> None:
        ws1 = chronica.run(theogony_ws, {}, seed=42)
        ws2 = chronica.run(theogony_ws, {}, seed=42)
        assert ws1.model_dump_json() == ws2.model_dump_json()

    def test_does_not_modify_input(self, theogony_ws: WorldState) -> None:
        # Check a lineage before
        radbot_before = theogony_ws.entities.get("lineage.radbot")
        element_before = radbot_before.element if radbot_before else None

        _ = chronica.run(theogony_ws, {}, seed=42)

        # Input should be unchanged
        radbot_after = theogony_ws.entities.get("lineage.radbot")
        element_after = radbot_after.element if radbot_after else None

        assert element_before == element_after
