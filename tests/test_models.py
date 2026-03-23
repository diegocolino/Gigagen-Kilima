"""Milestone 1 & 2 validation tests for Gigagen core models and worldpack."""

from __future__ import annotations

import json
import pathlib

import pytest

from gigagen.core.entity import (
    BaseEntity,
    Character,
    Faction,
    MacroFaction,
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

def _load_json_raw(name: str):
    return json.loads((WORLDS_DIR / name).read_text(encoding="utf-8"))


def _load_json(name: str) -> list[dict]:
    """Load a worldpack JSON, handling both plain arrays and object wrappers."""
    raw = _load_json_raw(name)
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ("characters", "relations", "locations", "macro_factions"):
            if key in raw:
                return raw[key]
    return []


def _normalize_location(raw: dict) -> dict:
    """Normalize new-format location fields to match the Location model."""
    d = dict(raw)
    if "level" in d and "zone_level" not in d:
        d["zone_level"] = d.pop("level")
    if "parent" in d and "parent_location_id" not in d:
        d["parent_location_id"] = d.pop("parent")
    if "faction_control" in d and "controlling_macro_faction_id" not in d:
        d["controlling_macro_faction_id"] = d.pop("faction_control")
    if "entity_type" not in d:
        d["entity_type"] = "location"
    if "canon_level" not in d:
        d["canon_level"] = "fixed"
    if "name" not in d:
        d["name"] = d.get("id", "")
    known = {
        "id", "entity_type", "name", "tags", "canon_level", "description",
        "tonic", "zone_level", "parent_location_id", "biome_tags",
        "status", "controlling_macro_faction_id", "secondary_macro_faction_ids",
        "tension", "access",
    }
    return {k: v for k, v in d.items() if k in known}


def _load_locations() -> list[dict]:
    """Load and normalize locations."""
    return [_normalize_location(loc) for loc in _load_json("locations.json")]


def _load_factions_data() -> list[dict]:
    """Load factions, reconstructing embedded structure from split format."""
    raw = _load_json_raw("factions.json")
    if isinstance(raw, dict) and "macro_factions" in raw:
        mfacs = list(raw["macro_factions"])
        facs_by_mfac: dict[str, list] = {}
        for f in raw.get("factions", []):
            mfid = f.get("macro_faction_id", "")
            facs_by_mfac.setdefault(mfid, []).append(f)
        result = []
        for mf in mfacs:
            mf_copy = dict(mf)
            mf_copy["factions"] = facs_by_mfac.get(mf_copy["id"], [])
            result.append(mf_copy)
        return result
    elif isinstance(raw, list):
        return raw
    return []


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


    def test_faction_assignments(self, characters: list[Character]) -> None:
        """Characters with known faction assignments have them set."""
        by_id = {c.id: c for c in characters}
        assert by_id["kilima_in12_rebel"].current_faction_id == "fac.red_fist_dragons"
        assert by_id["kilima_in12_deity"].current_faction_id == "fac.direnis_cell"
        assert by_id["kilima_in12_explorer"].current_faction_id == "fac.dust_parade"
        assert by_id["kilima_in12_hero"].current_faction_id == "fac.master_council"
        assert by_id["kilima_in12_leader"].current_faction_id == "fac.uc_interior"
        # Characters without known factions default to None
        assert by_id["kilima_in12_creator"].current_faction_id is None
        assert by_id["kilima_in12_orphan"].current_faction_id is None


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
        return [MacroFaction(**f) for f in _load_factions_data()]

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
            assert f.entity_type == "macro_faction"


# ---------------------------------------------------------------------------
# Location tests
# ---------------------------------------------------------------------------

class TestLocations:
    @pytest.fixture(scope="class")
    def locations(self) -> list[Location]:
        return [Location(**loc) for loc in _load_locations()]

    def test_load_all_locations(self, locations: list[Location]) -> None:
        assert len(locations) >= 15  # 55 in new hierarchical format

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

    def test_load_all_relations(self, relations: list[Relation]) -> None:
        assert len(relations) >= 26  # 30 after FL-4 update

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
        factions = [MacroFaction(**f) for f in _load_factions_data()]
        locations = [Location(**loc) for loc in _load_locations()]
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
            active_macro_faction_ids=[f.id for f in factions if f.status != "dissolved"],
            active_location_ids=[loc.id for loc in locations],
            tags=["nb1", "test"],
        )

    def test_entity_count(self, world_state: WorldState) -> None:
        assert len(world_state.entities) >= 37  # 12 chars + 10 facs + locations

    def test_relation_count(self, world_state: WorldState) -> None:
        assert len(world_state.relations) >= 26  # 30 after FL-4

    def test_seed(self, world_state: WorldState) -> None:
        assert world_state.seed == 1

    def test_reproducibility(self) -> None:
        """Same seed produces same WorldState."""
        def build(seed: int) -> str:
            characters = [Character(**c) for c in _load_json("characters.json")]
            factions = [MacroFaction(**f) for f in _load_factions_data()]
            locations = [Location(**loc) for loc in _load_locations()]
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
                active_macro_faction_ids=[f.id for f in factions],
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
        factions = [MacroFaction(**f) for f in _load_factions_data()]
        assert len(factions) == 10
        # Freya leads Anti Group (formerly The Resistance)
        anti = next(f for f in factions if f.id == "mfac.anti_group")
        assert anti.mode == "phrygian"
        assert anti.scale_family == "greek"

    def test_locations_json_includes_limbo_and_recess(self) -> None:
        locations = [Location(**loc) for loc in _load_locations()]
        ids = {loc.id for loc in locations}
        assert "loc.limbo" in ids, "The Limbo missing"
        assert "loc.recess" in ids, "The Recess missing"

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
        factions = [MacroFaction(**f) for f in _load_factions_data()]
        locations = [Location(**loc) for loc in _load_locations()]
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
            active_macro_faction_ids=[f.id for f in factions if f.status != "dissolved"],
            active_location_ids=[loc.id for loc in locations],
        )
        assert ws.world_id == "world.kilima"
        assert len(ws.entities) >= 37  # 12 chars + 10 facs + locations


# ---------------------------------------------------------------------------
# Faction invariant tests
# ---------------------------------------------------------------------------

class TestFactionInvariants:
    """Validate faction consistency invariant checks."""

    def _build_ws(
        self,
        chars: list[Character],
        facs: list[Faction],
    ) -> WorldState:
        locations = [Location(**loc) for loc in _load_locations()]
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
            active_macro_faction_ids=[f.id for f in facs],
            active_location_ids=[loc.id for loc in locations],
        )

    def test_valid_faction_passes(self) -> None:
        from gigagen.core.invariants import validate_invariants
        chars = [Character(**c) for c in _load_json("characters.json")]
        facs = [MacroFaction(**f) for f in _load_factions_data()]
        ws = self._build_ws(chars, facs)
        result = validate_invariants(ws, WORLDS_DIR / "invariants.json")
        # No faction-related errors
        sub_errors = [e for e in result.errors if "faction" in e.lower()]
        assert not sub_errors, f"Unexpected faction errors: {sub_errors}"

    def test_invalid_faction_name_fails(self) -> None:
        from gigagen.core.invariants import validate_invariants
        chars = [Character(**c) for c in _load_json("characters.json")]
        facs = [MacroFaction(**f) for f in _load_factions_data()]
        # Set a character to a non-existent faction
        rebel = next(c for c in chars if c.id == "kilima_in12_rebel")
        rebel.current_faction_id = "Nonexistent Cell"
        ws = self._build_ws(chars, facs)
        result = validate_invariants(ws, WORLDS_DIR / "invariants.json")
        assert not result.valid
        assert any("Nonexistent Cell" in e for e in result.errors)

    def test_faction_unknown_ref_fails(self) -> None:
        from gigagen.core.invariants import validate_invariants
        chars = [Character(**c) for c in _load_json("characters.json")]
        facs = [MacroFaction(**f) for f in _load_factions_data()]
        # Set a completely unknown faction reference
        rebel = next(c for c in chars if c.id == "kilima_in12_rebel")
        rebel.current_faction_id = "fac.totally_fake"
        rebel.current_macro_faction_id = None
        ws = self._build_ws(chars, facs)
        result = validate_invariants(ws, WORLDS_DIR / "invariants.json")
        assert not result.valid
        assert any("fac.totally_fake" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Location parent hierarchy invariant tests
# ---------------------------------------------------------------------------

class TestLocationParentInvariants:
    """Validate location parent hierarchy invariant checks."""

    def _build_ws_with_locations(self, locations: list[Location]) -> WorldState:
        chars = [Character(**c) for c in _load_json("characters.json")]
        facs = [MacroFaction(**f) for f in _load_factions_data()]
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
            active_macro_faction_ids=[f.id for f in facs],
            active_location_ids=[loc.id for loc in locations],
        )

    def test_valid_parents_pass(self) -> None:
        from gigagen.core.invariants import validate_invariants
        locations = [Location(**loc) for loc in _load_locations()]
        ws = self._build_ws_with_locations(locations)
        result = validate_invariants(ws, WORLDS_DIR / "invariants.json")
        parent_errors = [e for e in result.errors if "parent" in e.lower()]
        assert not parent_errors, f"Unexpected parent errors: {parent_errors}"

    def test_invalid_parent_reference_fails(self) -> None:
        from gigagen.core.invariants import validate_invariants
        locations = [Location(**loc) for loc in _load_locations()]
        # Point a location to a non-existent parent
        tower = next(l for l in locations if l.id == "loc.tower")
        tower.parent_location_id = "loc.nonexistent"
        ws = self._build_ws_with_locations(locations)
        result = validate_invariants(ws, WORLDS_DIR / "invariants.json")
        assert not result.valid
        assert any("loc.nonexistent" in e for e in result.errors)

    def test_parent_cycle_fails(self) -> None:
        from gigagen.core.invariants import validate_invariants
        locations = [Location(**loc) for loc in _load_locations()]
        # Create a cycle: capitol → agora → capitol
        capitol = next(l for l in locations if l.id == "capitol")
        agora = next(l for l in locations if l.id == "agora")
        capitol.parent_location_id = "agora"
        agora.parent_location_id = "capitol"
        ws = self._build_ws_with_locations(locations)
        result = validate_invariants(ws, WORLDS_DIR / "invariants.json")
        assert not result.valid
        assert any("cycle" in e.lower() for e in result.errors)
