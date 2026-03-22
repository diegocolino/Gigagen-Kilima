"""Milestone 1 & 2 validation tests for Gigagen core models and worldpack."""

from __future__ import annotations

import json
import pathlib

import pytest

from gigagen.core.entity import (
    BaseEntity,
    Character,
    Faction,
    Location,
    Item,
    Anima,
)
from gigagen.core.relation import Relation, harmonic_affinity
from gigagen.core.world_state import WorldState


WORLDS_DIR = pathlib.Path(__file__).resolve().parent.parent / "worlds" / "kilima"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(name: str) -> list[dict]:
    return json.loads((WORLDS_DIR / name).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Character tests
# ---------------------------------------------------------------------------

class TestCharacters:
    @pytest.fixture(scope="class")
    def characters(self) -> list[Character]:
        return [Character(**c) for c in _load_json("characters.json")]

    def test_load_all_12(self, characters: list[Character]) -> None:
        assert len(characters) == 12

    def test_all_archetypes_present(self, characters: list[Character]) -> None:
        codes = {c.archetype for c in characters}
        expected = {"CAR", "JES", "HER", "REB", "ORP", "LOV",
                    "HCK", "LEA", "INN", "EXP", "CRE", "DEI"}
        assert codes == expected

    def test_all_notes_present(self, characters: list[Character]) -> None:
        notes = {c.note for c in characters}
        expected = {"C", "C#", "D", "D#", "E", "F",
                    "F#", "G", "G#", "A", "A#", "B"}
        assert notes == expected

    def test_entity_type(self, characters: list[Character]) -> None:
        for c in characters:
            assert c.entity_type == "character"


    def test_subdivision_assignments(self, characters: list[Character]) -> None:
        """Characters with known subdivision assignments have them set."""
        by_id = {c.id: c for c in characters}
        assert by_id["char.rebel"].current_subdivision_id == "Red Fist Dragons"
        assert by_id["char.deity"].current_subdivision_id == "Direnis Cell"
        assert by_id["char.explorer"].current_subdivision_id == "Dust Parade"
        assert by_id["char.hero"].current_subdivision_id == "Master Council"
        assert by_id["char.leader"].current_subdivision_id == "Interior"
        assert by_id["char.creator"].current_subdivision_id == "Forno Cell"
        # Characters without known subdivisions default to None
        assert by_id["char.orphan"].current_subdivision_id is None
        assert by_id["char.hacker"].current_subdivision_id is None


class TestCharacterValidation:
    def test_accepts_any_archetype_string(self) -> None:
        """Archetype validation is now catalog-based, not hardcoded."""
        c = Character(
            id="char.test",
            name="Test",
            canon_level="fixed",
            archetype="CUSTOM",
            note="X",
            hero_type="test",
            civil_name="Test",
            role_name="Test",
            current_location_id="loc.x",
        )
        assert c.archetype == "CUSTOM"
        assert c.note == "X"

    def test_reject_missing_required_fields(self) -> None:
        with pytest.raises(Exception):
            Character(id="char.test", name="Test")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Faction tests
# ---------------------------------------------------------------------------

class TestFactions:
    @pytest.fixture(scope="class")
    def factions(self) -> list[Faction]:
        return [Faction(**f) for f in _load_json("factions.json")]

    def test_load_all_10(self, factions: list[Faction]) -> None:
        assert len(factions) == 10

    def test_includes_anti_group(self, factions: list[Faction]) -> None:
        names = {f.name for f in factions}
        assert "Anti Group" in names

    def test_no_ai_faction(self, factions: list[Faction]) -> None:
        """Flai is NOT a faction — it operates through Union Corp and Agency SL."""
        names = {f.name for f in factions}
        assert "The AI" not in names

    def test_all_have_harmonic_fields(self, factions: list[Faction]) -> None:
        for f in factions:
            assert f.mode, f"{f.id} missing mode"
            assert f.intervals, f"{f.id} missing intervals"
            assert f.note_count > 0, f"{f.id} missing note_count"
            assert f.scale_family, f"{f.id} missing scale_family"

    def test_entity_type(self, factions: list[Faction]) -> None:
        for f in factions:
            assert f.entity_type == "faction"


# ---------------------------------------------------------------------------
# Location tests
# ---------------------------------------------------------------------------

class TestLocations:
    @pytest.fixture(scope="class")
    def locations(self) -> list[Location]:
        return [Location(**loc) for loc in _load_json("locations.json")]

    def test_load_all_15(self, locations: list[Location]) -> None:
        assert len(locations) == 15

    def test_entity_type(self, locations: list[Location]) -> None:
        for loc in locations:
            assert loc.entity_type == "location"


# ---------------------------------------------------------------------------
# Relation tests
# ---------------------------------------------------------------------------

class TestRelations:
    @pytest.fixture(scope="class")
    def relations(self) -> list[Relation]:
        return [Relation(**r) for r in _load_json("relations.json")]

    def test_load_all_26(self, relations: list[Relation]) -> None:
        assert len(relations) == 26

    def test_all_kinds_valid(self, relations: list[Relation]) -> None:
        from gigagen.core.relation import RELATION_KINDS
        for r in relations:
            assert r.kind in RELATION_KINDS

    def test_reject_invalid_kind(self) -> None:
        with pytest.raises(ValueError, match="Invalid relation kind"):
            Relation(
                id="rel.test",
                source_id="char.a",
                target_id="char.b",
                kind="INVALID_KIND",
                weight=0.5,
                polarity=0,
                canon_level="fixed",
            )


# ---------------------------------------------------------------------------
# Harmonic affinity tests
# ---------------------------------------------------------------------------

class TestHarmonicAffinity:
    def test_unison(self) -> None:
        assert harmonic_affinity("C", "C") == 1.0

    def test_tritone(self) -> None:
        assert harmonic_affinity("C", "F#") == -1.0

    def test_perfect_fifth(self) -> None:
        assert harmonic_affinity("C", "G") == 0.9

    def test_minor_2nd_strong_tension(self) -> None:
        """D# → E = 1 semitone = minor 2nd / strong tension."""
        val = harmonic_affinity("D#", "E")
        assert val < 0, "Minor 2nd should be negative (tension)"
        assert val == pytest.approx(-0.8, abs=0.3)

    def test_minor_6th_melancholy(self) -> None:
        """D# → B = 8 semitones = minor 6th / melancholy."""
        val = harmonic_affinity("D#", "B")
        assert val < 0, "Minor 6th should be slightly negative (melancholy)"
        assert val == pytest.approx(-0.2, abs=0.3)

    def test_range(self) -> None:
        """All results must be in [-1.0, 1.0]."""
        notes = ["C", "C#", "D", "D#", "E", "F",
                 "F#", "G", "G#", "A", "A#", "B"]
        for a in notes:
            for b in notes:
                val = harmonic_affinity(a, b)
                assert -1.0 <= val <= 1.0

    def test_unknown_note_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown note"):
            harmonic_affinity("X", "C")

    def test_enharmonic_equivalents(self) -> None:
        assert harmonic_affinity("C#", "G") == harmonic_affinity("Db", "G")


# ---------------------------------------------------------------------------
# WorldState tests
# ---------------------------------------------------------------------------

class TestWorldState:
    @pytest.fixture(scope="class")
    def world_state(self) -> WorldState:
        characters = [Character(**c) for c in _load_json("characters.json")]
        factions = [Faction(**f) for f in _load_json("factions.json")]
        locations = [Location(**loc) for loc in _load_json("locations.json")]
        relations = [Relation(**r) for r in _load_json("relations.json")]

        entities: dict[str, BaseEntity] = {}
        for ent in [*characters, *factions, *locations]:
            entities[ent.id] = ent

        return WorldState(
            world_id="world.kilima",
            seed=1,
            phase="block_1_start",
            description="Kilima NB1 — seed 1",
            entities=entities,
            relations=relations,
            active_faction_ids=[f.id for f in factions if f.status != "dissolved"],
            active_location_ids=[loc.id for loc in locations],
            tags=["nb1", "test"],
        )

    def test_entity_count(self, world_state: WorldState) -> None:
        assert len(world_state.entities) == 12 + 10 + 15  # chars + facs + locs

    def test_relation_count(self, world_state: WorldState) -> None:
        assert len(world_state.relations) == 26

    def test_seed(self, world_state: WorldState) -> None:
        assert world_state.seed == 1

    def test_reproducibility(self) -> None:
        """Same seed produces same WorldState."""
        def build(seed: int) -> str:
            characters = [Character(**c) for c in _load_json("characters.json")]
            factions = [Faction(**f) for f in _load_json("factions.json")]
            locations = [Location(**loc) for loc in _load_json("locations.json")]
            relations = [Relation(**r) for r in _load_json("relations.json")]

            entities: dict[str, BaseEntity] = {}
            for ent in [*characters, *factions, *locations]:
                entities[ent.id] = ent

            ws = WorldState(
                world_id="world.kilima",
                seed=seed,
                phase="block_1_start",
                entities=entities,
                relations=relations,
                active_faction_ids=[f.id for f in factions],
                active_location_ids=[loc.id for loc in locations],
            )
            return ws.model_dump_json()

        assert build(42) == build(42)
        # Different seeds still load the same fixed data (variation comes later)
        assert build(1) != build(2)  # seed field differs


# ---------------------------------------------------------------------------
# Milestone 2 — Worldpack completeness tests
# ---------------------------------------------------------------------------

class TestWorldpackFiles:
    """Verify all M2 deliverables exist and validate."""

    def test_world_json_exists(self) -> None:
        path = WORLDS_DIR / "world.json"
        assert path.exists(), "world.json missing"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["world_id"] == "world.kilima"

    def test_characters_json_validates(self) -> None:
        chars = [Character(**c) for c in _load_json("characters.json")]
        assert len(chars) == 12
        # All have hero_type (M2 requirement)
        for c in chars:
            assert c.hero_type, f"{c.id} missing hero_type"

    def test_factions_json_with_corrected_leadership(self) -> None:
        factions = [Faction(**f) for f in _load_json("factions.json")]
        assert len(factions) == 10
        # Freya leads Anti Group (formerly The Resistance)
        anti = next(f for f in factions if f.id == "fac.anti_group")
        assert anti.mode == "phrygian"
        assert anti.scale_family == "greek"

    def test_locations_json_includes_limbo_and_forno(self) -> None:
        locations = [Location(**loc) for loc in _load_json("locations.json")]
        ids = {loc.id for loc in locations}
        assert "loc.limbo" in ids, "The Limbo missing"
        assert "loc.forno" in ids, "The Forno missing"

    def test_relations_json_validates(self) -> None:
        relations = [Relation(**r) for r in _load_json("relations.json")]
        assert len(relations) >= 15, "Need at least 15 core relations"

    def test_invariant_relations_exist_in_relations_json(self) -> None:
        """Every fixed relationship declared in invariants.json must have
        a matching entry in relations.json (same source, target, kind)."""
        inv = json.loads(
            (WORLDS_DIR / "invariants.json").read_text(encoding="utf-8")
        )
        rel_data = _load_json("relations.json")
        rel_triples = {
            (r["source_id"], r["target_id"], r["kind"]) for r in rel_data
        }
        missing = []
        for entry in inv["fixed"]["relationships"]:
            triple = (entry["source"], entry["target"], entry["kind"])
            if triple not in rel_triples:
                missing.append(triple)
        assert not missing, f"Relations in invariants.json missing from relations.json: {missing}"

    def test_invariants_json_exists(self) -> None:
        path = WORLDS_DIR / "invariants.json"
        assert path.exists(), "invariants.json missing"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "fixed" in data
        assert "forbidden" in data
        assert "variables" in data
        assert len(data["variables"]) == 3

    def test_timeline_bn1_exists(self) -> None:
        path = WORLDS_DIR / "timelines" / "bn1.yaml"
        assert path.exists(), "timelines/bn1.yaml missing"
        content = path.read_text(encoding="utf-8")
        assert "version:" in content
        assert "events:" in content

    def test_all_jsons_validate_against_models(self) -> None:
        """Full integration: load every JSON and build a WorldState."""
        characters = [Character(**c) for c in _load_json("characters.json")]
        factions = [Faction(**f) for f in _load_json("factions.json")]
        locations = [Location(**loc) for loc in _load_json("locations.json")]
        relations = [Relation(**r) for r in _load_json("relations.json")]

        entities: dict[str, BaseEntity] = {}
        for ent in [*characters, *factions, *locations]:
            entities[ent.id] = ent

        ws = WorldState(
            world_id="world.kilima",
            seed=1,
            phase="block_1_start",
            entities=entities,
            relations=relations,
            active_faction_ids=[f.id for f in factions if f.status != "dissolved"],
            active_location_ids=[loc.id for loc in locations],
        )
        assert ws.world_id == "world.kilima"
        assert len(ws.entities) == 37  # 12 + 10 + 15


# ---------------------------------------------------------------------------
# Subdivision invariant tests
# ---------------------------------------------------------------------------

class TestSubdivisionInvariants:
    """Validate subdivision consistency invariant checks."""

    def _build_ws(
        self,
        chars: list[Character],
        facs: list[Faction],
    ) -> WorldState:
        locations = [Location(**loc) for loc in _load_json("locations.json")]
        relations = [Relation(**r) for r in _load_json("relations.json")]
        entities: dict[str, BaseEntity] = {}
        for ent in [*chars, *facs, *locations]:
            entities[ent.id] = ent
        return WorldState(
            world_id="world.kilima",
            seed=1,
            phase="block_1_start",
            entities=entities,
            relations=relations,
            active_faction_ids=[f.id for f in facs],
            active_location_ids=[loc.id for loc in locations],
        )

    def test_valid_subdivision_passes(self) -> None:
        from gigagen.core.invariants import validate_invariants
        chars = [Character(**c) for c in _load_json("characters.json")]
        facs = [Faction(**f) for f in _load_json("factions.json")]
        ws = self._build_ws(chars, facs)
        result = validate_invariants(ws, WORLDS_DIR / "invariants.json")
        # No subdivision-related errors
        sub_errors = [e for e in result.errors if "subdivision" in e.lower()]
        assert not sub_errors, f"Unexpected subdivision errors: {sub_errors}"

    def test_invalid_subdivision_name_fails(self) -> None:
        from gigagen.core.invariants import validate_invariants
        chars = [Character(**c) for c in _load_json("characters.json")]
        facs = [Faction(**f) for f in _load_json("factions.json")]
        # Set a character to a non-existent subdivision
        rebel = next(c for c in chars if c.id == "char.rebel")
        rebel.current_subdivision_id = "Nonexistent Cell"
        ws = self._build_ws(chars, facs)
        result = validate_invariants(ws, WORLDS_DIR / "invariants.json")
        assert not result.valid
        assert any("Nonexistent Cell" in e for e in result.errors)

    def test_subdivision_without_faction_fails(self) -> None:
        from gigagen.core.invariants import validate_invariants
        chars = [Character(**c) for c in _load_json("characters.json")]
        facs = [Faction(**f) for f in _load_json("factions.json")]
        # Set subdivision but clear faction
        rebel = next(c for c in chars if c.id == "char.rebel")
        rebel.current_subdivision_id = "Red Fist Dragons"
        rebel.current_faction_id = None
        ws = self._build_ws(chars, facs)
        result = validate_invariants(ws, WORLDS_DIR / "invariants.json")
        assert not result.valid
        assert any("no faction" in e.lower() for e in result.errors)


# ---------------------------------------------------------------------------
# Location parent hierarchy invariant tests
# ---------------------------------------------------------------------------

class TestLocationParentInvariants:
    """Validate location parent hierarchy invariant checks."""

    def _build_ws_with_locations(self, locations: list[Location]) -> WorldState:
        chars = [Character(**c) for c in _load_json("characters.json")]
        facs = [Faction(**f) for f in _load_json("factions.json")]
        relations = [Relation(**r) for r in _load_json("relations.json")]
        entities: dict[str, BaseEntity] = {}
        for ent in [*chars, *facs, *locations]:
            entities[ent.id] = ent
        return WorldState(
            world_id="world.kilima",
            seed=1,
            phase="block_1_start",
            entities=entities,
            relations=relations,
            active_faction_ids=[f.id for f in facs],
            active_location_ids=[loc.id for loc in locations],
        )

    def test_valid_parents_pass(self) -> None:
        from gigagen.core.invariants import validate_invariants
        locations = [Location(**loc) for loc in _load_json("locations.json")]
        ws = self._build_ws_with_locations(locations)
        result = validate_invariants(ws, WORLDS_DIR / "invariants.json")
        parent_errors = [e for e in result.errors if "parent" in e.lower()]
        assert not parent_errors, f"Unexpected parent errors: {parent_errors}"

    def test_invalid_parent_reference_fails(self) -> None:
        from gigagen.core.invariants import validate_invariants
        locations = [Location(**loc) for loc in _load_json("locations.json")]
        # Point a location to a non-existent parent
        tower = next(l for l in locations if l.id == "loc.tower")
        tower.parent_location_id = "loc.nonexistent"
        ws = self._build_ws_with_locations(locations)
        result = validate_invariants(ws, WORLDS_DIR / "invariants.json")
        assert not result.valid
        assert any("loc.nonexistent" in e for e in result.errors)

    def test_parent_cycle_fails(self) -> None:
        from gigagen.core.invariants import validate_invariants
        locations = [Location(**loc) for loc in _load_json("locations.json")]
        # Create a cycle: capital → city → capital
        capital = next(l for l in locations if l.id == "loc.capital")
        city = next(l for l in locations if l.id == "loc.city")
        capital.parent_location_id = "loc.city"
        city.parent_location_id = "loc.capital"
        ws = self._build_ws_with_locations(locations)
        result = validate_invariants(ws, WORLDS_DIR / "invariants.json")
        assert not result.valid
        assert any("cycle" in e.lower() for e in result.errors)
