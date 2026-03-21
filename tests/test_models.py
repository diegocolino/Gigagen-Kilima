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


class TestCharacterValidation:
    def test_reject_wrong_archetype(self) -> None:
        with pytest.raises(ValueError, match="Invalid archetype"):
            Character(
                id="char.test",
                name="Test",
                canon_level="fixed",
                archetype="WRONG",
                note="C",
                hero_type="test",
                civil_name="Test",
                role_name="Test",
                current_location_id="loc.x",
            )

    def test_reject_wrong_note(self) -> None:
        with pytest.raises(ValueError, match="Invalid note"):
            Character(
                id="char.test",
                name="Test",
                canon_level="fixed",
                archetype="REB",
                note="Z",
                hero_type="test",
                civil_name="Test",
                role_name="Test",
                current_location_id="loc.x",
            )

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

    def test_load_all_4(self, factions: list[Faction]) -> None:
        assert len(factions) == 4

    def test_includes_ai(self, factions: list[Faction]) -> None:
        names = {f.name for f in factions}
        assert "The AI" in names

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

    def test_load_all_27(self, relations: list[Relation]) -> None:
        assert len(relations) == 27

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
        assert len(world_state.entities) == 12 + 4 + 15  # chars + facs + locs

    def test_relation_count(self, world_state: WorldState) -> None:
        assert len(world_state.relations) == 27

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
        assert len(factions) == 4
        resistance = next(f for f in factions if f.id == "fac.resistencia")
        assert resistance.leader_id == "char.deity", "Freya should lead Resistance"

    def test_locations_json_includes_limbo_and_forno(self) -> None:
        locations = [Location(**loc) for loc in _load_json("locations.json")]
        ids = {loc.id for loc in locations}
        assert "loc.limbo" in ids, "The Limbo missing"
        assert "loc.forno" in ids, "The Forno missing"

    def test_relations_json_validates(self) -> None:
        relations = [Relation(**r) for r in _load_json("relations.json")]
        assert len(relations) >= 15, "Need at least 15 core relations"

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
        assert len(ws.entities) == 31  # 12 + 4 + 15
