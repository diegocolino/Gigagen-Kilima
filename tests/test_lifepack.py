"""LP-1 tests for the LifePack Pydantic model."""

from __future__ import annotations

import json
import pathlib

import pytest

from gigagen.core.lifepack import (
    LifePack,
    LifePackMeta,
    LifePackOctave,
    LifePackSlot,
    build_empty_lifepack,
    change_mode,
    get_interval_semitones,
    populate_octave_7,
    resolve_note,
    resolve_octave_8_invariants,
    resolve_octave_8_variable,
    ElementConfig,
    compute_available_anima_slots,
    load_elements_catalog,
)

DOCS_DIR = pathlib.Path("docs")


# ---------------------------------------------------------------------------
# resolve_note
# ---------------------------------------------------------------------------


class TestResolveNote:
    def test_unison(self) -> None:
        assert resolve_note(0, 0) == "C"

    def test_fifth_from_c(self) -> None:
        assert resolve_note(0, 7) == "G"

    def test_fifth_from_d_sharp(self) -> None:
        # D# (3) + 7 = 10 = A#
        assert resolve_note(3, 7) == "A#"

    def test_tritone_from_c(self) -> None:
        assert resolve_note(0, 6) == "F#"

    def test_wraps_around(self) -> None:
        # B (11) + 1 = 0 = C
        assert resolve_note(11, 1) == "C"

    def test_all_12_from_c(self) -> None:
        expected = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        for i, note in enumerate(expected):
            assert resolve_note(0, i) == note


# ---------------------------------------------------------------------------
# Model instantiation
# ---------------------------------------------------------------------------


class TestLifePackSlot:
    def test_empty_slot(self) -> None:
        slot = LifePackSlot()
        assert slot.entity_id is None
        assert slot.locked is False
        assert slot.unlocked is True

    def test_chord_slot(self) -> None:
        slot = LifePackSlot(
            interval="5J",
            semitones=7,
            role="location_pilar",
            entity_id="loc.cave",
            entity_name="The Cave",
            resolved_note="A#",
            alteration="perfect",
        )
        assert slot.semitones == 7
        assert slot.resolved_note == "A#"

    def test_locked_slot(self) -> None:
        slot = LifePackSlot(locked=True, unlocked=False)
        assert slot.locked is True
        assert slot.unlocked is False


class TestLifePackOctave:
    def test_empty_octave(self) -> None:
        octave = LifePackOctave()
        assert octave.slots == {}

    def test_octave_with_slots(self) -> None:
        octave = LifePackOctave(
            unlocked_at="contempo",
            logic="internal_chord",
            slots={
                "0_tonica": LifePackSlot(interval="unison", semitones=0),
                "7_quinta_justa": LifePackSlot(interval="5J", semitones=7),
            },
        )
        assert len(octave.slots) == 2
        assert octave.logic == "internal_chord"


class TestLifePackMeta:
    def test_default_meta(self) -> None:
        meta = LifePackMeta()
        assert meta.tonic == ""
        assert meta.tonic_semitone is None

    def test_kive_meta(self) -> None:
        meta = LifePackMeta(
            entity_id="kilima_in12_rebel",
            entity_name="Kive",
            collection="kilima_in12",
            tonic="D#",
            tonic_semitone=3,
            mode="minor",
        )
        assert meta.tonic == "D#"
        assert meta.tonic_semitone == 3


# ---------------------------------------------------------------------------
# build_empty_lifepack
# ---------------------------------------------------------------------------


class TestBuildEmptyLifepack:
    def test_builds_for_kive(self) -> None:
        lp = build_empty_lifepack("D#")
        assert lp.meta.tonic == "D#"
        assert lp.meta.tonic_semitone == 3

    def test_lore_has_12_slots(self) -> None:
        lp = build_empty_lifepack("C")
        assert len(lp.octave_0_lore.slots) == 12

    def test_chord_octaves_have_12_slots(self) -> None:
        lp = build_empty_lifepack("C")
        assert len(lp.octave_3_locations.slots) == 12
        assert len(lp.octave_4_objetos.slots) == 12
        assert len(lp.octave_5_skills.slots) == 12

    def test_chord_4_initially_unlocked(self) -> None:
        lp = build_empty_lifepack("C")
        unlocked = [
            k for k, s in lp.octave_3_locations.slots.items() if not s.locked
        ]
        assert len(unlocked) == 4

    def test_character_octave_all_unlocked(self) -> None:
        lp = build_empty_lifepack("C")
        for slot in lp.octave_7_personajes.slots.values():
            assert slot.locked is False

    def test_resolved_notes_correct(self) -> None:
        lp = build_empty_lifepack("D#")  # D# = semitone 3
        # 5J = +7 semitones → 3+7 = 10 = A#
        fifth = lp.octave_3_locations.slots["7_quinta_justa"]
        assert fifth.resolved_note == "A#"
        # Tritone = +6 → 3+6 = 9 = A
        tritone = lp.octave_3_locations.slots["6_tritono"]
        assert tritone.resolved_note == "A"

    def test_invalid_tonic_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown tonic"):
            build_empty_lifepack("X")

    def test_lineage_slot_has_tonic(self) -> None:
        lp = build_empty_lifepack("F#")
        lineage = lp.octave_2_linajes.slots["0_tonica"]
        assert lineage.note == "F#"
        assert lineage.semitone == 6

    def test_get_octave_by_index(self) -> None:
        lp = build_empty_lifepack("C")
        assert lp.get_octave(7).logic == "full_12_by_interval"
        assert lp.get_octave(0).logic == "fixed_12_archetypes"

    def test_get_octave_invalid_index(self) -> None:
        lp = build_empty_lifepack("C")
        with pytest.raises(ValueError):
            lp.get_octave(9)


# ---------------------------------------------------------------------------
# JSON serialization round-trip
# ---------------------------------------------------------------------------


class TestSerialization:
    def test_round_trip(self) -> None:
        lp = build_empty_lifepack("D#", mode="minor")
        json_str = lp.model_dump_json(indent=2)
        loaded = LifePack.model_validate_json(json_str)
        assert loaded.meta.tonic == "D#"
        assert loaded.meta.mode == "minor"
        assert len(loaded.octave_7_personajes.slots) == 12

    def test_to_dict_and_back(self) -> None:
        lp = build_empty_lifepack("B")
        data = lp.model_dump(mode="json")
        restored = LifePack.model_validate(data)
        assert restored.meta.tonic == "B"

    def test_validate_template_json(self) -> None:
        """LP-1 success criterion: template JSON validates."""
        template_path = DOCS_DIR / "gigagen_lifepack_template.json"
        if not template_path.exists():
            pytest.skip("Template file not found")
        raw = json.loads(template_path.read_text(encoding="utf-8"))
        lp = LifePack.model_validate(raw)
        assert lp.octave_7_personajes.logic == "full_12_by_interval"
        assert len(lp.octave_7_personajes.slots) == 12

    def test_validate_kive_lifepack(self) -> None:
        """Kive's partially filled Life Pack validates."""
        kive_path = DOCS_DIR / "kilima_in12_rebel_lifepack.json"
        if not kive_path.exists():
            pytest.skip("Kive lifepack not found")
        raw = json.loads(kive_path.read_text(encoding="utf-8"))
        lp = LifePack.model_validate(raw)
        assert lp.meta.entity_id != ""
        assert lp.meta.tonic != ""


# ---------------------------------------------------------------------------
# LP-3: Mode (major/minor)
# ---------------------------------------------------------------------------


class TestGetIntervalSemitones:
    def test_third_minor(self) -> None:
        assert get_interval_semitones("3rd", "minor") == 3

    def test_third_major(self) -> None:
        assert get_interval_semitones("3rd", "major") == 4

    def test_sixth_minor(self) -> None:
        assert get_interval_semitones("6th", "minor") == 8

    def test_sixth_major(self) -> None:
        assert get_interval_semitones("6th", "major") == 9

    def test_seventh_minor(self) -> None:
        assert get_interval_semitones("7th", "minor") == 10

    def test_seventh_major(self) -> None:
        assert get_interval_semitones("7th", "major") == 11

    def test_invalid_degree(self) -> None:
        with pytest.raises(ValueError, match="Unknown degree"):
            get_interval_semitones("5th", "minor")

    def test_invalid_mode(self) -> None:
        with pytest.raises(ValueError, match="Unknown mode"):
            get_interval_semitones("3rd", "dorian")


class TestChangeMode:
    def test_minor_to_major_updates_meta(self) -> None:
        lp = build_empty_lifepack("D#", mode="minor")
        result = change_mode(lp, "major")
        assert result.meta.mode == "major"
        assert lp.meta.mode == "minor"  # original unchanged

    def test_same_mode_returns_copy(self) -> None:
        lp = build_empty_lifepack("C", mode="minor")
        result = change_mode(lp, "minor")
        assert result.meta.mode == "minor"
        assert result is not lp  # new object

    def test_third_slots_swap_semitones(self) -> None:
        lp = build_empty_lifepack("C", mode="minor")
        # In minor: tercera_menor=3, tercera_mayor=4
        assert lp.octave_3_locations.slots["3_tercera_menor"].semitones == 3
        assert lp.octave_3_locations.slots["4_tercera_mayor"].semitones == 4

        result = change_mode(lp, "major")
        # In major: slots swap semitones
        assert result.octave_3_locations.slots["3_tercera_menor"].semitones == 4
        assert result.octave_3_locations.slots["4_tercera_mayor"].semitones == 3

    def test_sixth_slots_swap(self) -> None:
        lp = build_empty_lifepack("C", mode="minor")
        result = change_mode(lp, "major")
        assert result.octave_4_objetos.slots["8_sexta_menor"].semitones == 9
        assert result.octave_4_objetos.slots["9_sexta_mayor"].semitones == 8

    def test_seventh_slots_swap(self) -> None:
        lp = build_empty_lifepack("C", mode="minor")
        result = change_mode(lp, "major")
        assert result.octave_5_skills.slots["10_septima_menor"].semitones == 11
        assert result.octave_5_skills.slots["11_septima_mayor"].semitones == 10

    def test_resolved_notes_recalculated(self) -> None:
        # D# minor: tercera_menor at 3 semitones = F#
        lp = build_empty_lifepack("D#", mode="minor")
        assert lp.octave_3_locations.slots["3_tercera_menor"].resolved_note == "F#"

        # After change to major: tercera_menor now has 4 semitones = G
        result = change_mode(lp, "major")
        assert result.octave_3_locations.slots["3_tercera_menor"].resolved_note == "G"

    def test_entities_preserved(self) -> None:
        """change_mode does not lose entity bindings."""
        lp = build_empty_lifepack("D#", mode="minor")
        # Bind an entity to a mode-sensitive slot
        lp.octave_3_locations.slots["3_tercera_menor"].entity_id = "loc.cave"
        lp.octave_3_locations.slots["3_tercera_menor"].entity_name = "The Cave"

        result = change_mode(lp, "major")
        slot = result.octave_3_locations.slots["3_tercera_menor"]
        assert slot.entity_id == "loc.cave"
        assert slot.entity_name == "The Cave"
        # But the note changed
        assert slot.resolved_note != lp.octave_3_locations.slots["3_tercera_menor"].resolved_note

    def test_all_3_chord_octaves_affected(self) -> None:
        lp = build_empty_lifepack("C", mode="minor")
        result = change_mode(lp, "major")
        # All 3 chord octaves should have swapped thirds
        for octave_name in ("octave_3_locations", "octave_4_objetos", "octave_5_skills"):
            octave = getattr(result, octave_name)
            assert octave.slots["3_tercera_menor"].semitones == 4

    def test_double_change_restores_original(self) -> None:
        lp = build_empty_lifepack("D#", mode="minor")
        major = change_mode(lp, "major")
        restored = change_mode(major, "minor")
        # Should be back to original semitones
        assert restored.octave_3_locations.slots["3_tercera_menor"].semitones == 3
        assert restored.octave_3_locations.slots["3_tercera_menor"].resolved_note == "F#"

    def test_invalid_mode_raises(self) -> None:
        lp = build_empty_lifepack("C")
        with pytest.raises(ValueError):
            change_mode(lp, "dorian")


# ---------------------------------------------------------------------------
# LP-4: Octave 7 auto-population
# ---------------------------------------------------------------------------


class TestPopulateOctave7:
    @staticmethod
    def _make_chars(notes: dict[str, str]) -> list[tuple[str, str, str]]:
        """Helper: {name: note} → [(id, name, note), ...]"""
        return [(f"char.{n.lower()}", n, note) for n, note in notes.items()]

    def test_12_characters_fill_all_slots(self) -> None:
        lp = build_empty_lifepack("C")
        chars = self._make_chars({
            "Zero": "C", "One": "C#", "Two": "D", "Three": "D#",
            "Four": "E", "Five": "F", "Six": "F#", "Seven": "G",
            "Eight": "G#", "Nine": "A", "Ten": "A#", "Eleven": "B",
        })
        populate_octave_7(lp, chars)
        filled = [
            k for k, s in lp.octave_7_personajes.slots.items()
            if isinstance(s, LifePackSlot) and s.entity_id
        ]
        assert len(filled) == 12

    def test_6_characters_leave_6_empty(self) -> None:
        lp = build_empty_lifepack("C")
        chars = self._make_chars({
            "Zero": "C", "Two": "D", "Four": "E",
            "Five": "F", "Seven": "G", "Nine": "A",
        })
        populate_octave_7(lp, chars)
        filled = [
            k for k, s in lp.octave_7_personajes.slots.items()
            if isinstance(s, LifePackSlot) and s.entity_id
        ]
        assert len(filled) == 6

    def test_kive_has_len_at_slot_1(self) -> None:
        """D# tonic, Len=E → interval 1 → 1_segunda_menor."""
        lp = build_empty_lifepack("D#")
        chars = [("kilima_in12_orphan", "Len", "E")]
        populate_octave_7(lp, chars)
        slot = lp.octave_7_personajes.slots["1_segunda_menor"]
        assert slot.entity_name == "Len"
        assert slot.entity_id == "kilima_in12_orphan"

    def test_kive_has_dev_at_slot_3(self) -> None:
        """D# tonic, Dev=F# → interval 3 → 3_tercera_menor."""
        lp = build_empty_lifepack("D#")
        chars = [("kilima_in12_hacker", "Dev", "F#")]
        populate_octave_7(lp, chars)
        slot = lp.octave_7_personajes.slots["3_tercera_menor"]
        assert slot.entity_name == "Dev"

    def test_kive_has_cris_at_slot_7(self) -> None:
        """D# tonic, Cris=A# → interval 7 → 7_quinta_justa."""
        lp = build_empty_lifepack("D#")
        chars = [("kilima_in12_creator", "Cris", "A#")]
        populate_octave_7(lp, chars)
        slot = lp.octave_7_personajes.slots["7_quinta_justa"]
        assert slot.entity_name == "Cris"

    def test_owner_at_unison(self) -> None:
        """Owner (same note as tonic) lands on slot 0."""
        lp = build_empty_lifepack("D#")
        chars = [("kilima_in12_rebel", "Kive", "D#")]
        populate_octave_7(lp, chars)
        slot = lp.octave_7_personajes.slots["0_tonica"]
        assert slot.entity_name == "Kive"

    def test_preserves_resolved_note(self) -> None:
        """Populating doesn't overwrite resolved_note."""
        lp = build_empty_lifepack("D#")
        chars = [("kilima_in12_orphan", "Len", "E")]
        populate_octave_7(lp, chars)
        slot = lp.octave_7_personajes.slots["1_segunda_menor"]
        assert slot.resolved_note == "E"  # D# + 1 = E
        assert slot.entity_note == "E"


class TestPopulateOctave7ViaLoader:
    def test_kilima_kive_auto_populated(self) -> None:
        """LP-4 success criterion: loader auto-populates octave 7."""
        from gigagen.io.load_worldpack import load_worldpack
        ws = load_worldpack(pathlib.Path("worlds/kilima"), seed=1)
        lp = ws.get_lifepack("kilima_in12_rebel")
        assert lp is not None

        # Len at slot 1
        assert lp.octave_7_personajes.slots["1_segunda_menor"].entity_name == "Len"
        # Dev at slot 3
        assert lp.octave_7_personajes.slots["3_tercera_menor"].entity_name == "Dev"
        # Cris at slot 7
        assert lp.octave_7_personajes.slots["7_quinta_justa"].entity_name == "Cris"


# ---------------------------------------------------------------------------
# LP-5: Unlock slots in simulation
# ---------------------------------------------------------------------------


class TestUnlockLifepackSlot:
    @staticmethod
    def _build_sim_with_lifepack():
        """Build a minimal WorldState + SimulatorState with a lifepack."""
        from gigagen.core.entity import Character
        from gigagen.core.lifepack import LifePack
        from gigagen.core.simulator import SimulatorState, _init_outcomes
        from gigagen.core.world_state import WorldState

        lp = build_empty_lifepack("D#", mode="minor")
        # Slot 8_sexta_menor should be locked
        assert lp.octave_3_locations.slots["8_sexta_menor"].locked is True

        char = Character(
            id="kilima_in12_rebel",
            entity_type="character",
            name="Kive",
            canon_level="fixed",
            archetype="REB",
            note="D#",
            hero_type="tragic_hero",
            civil_name="Kive",
            role_name="The Rebel",
            status="active",
            current_location_id="loc.cave",
            emotional_load="neutral",
        )

        ws = WorldState(
            world_id="test",
            seed=1,
            phase="test",
            entities={"kilima_in12_rebel": char},
            lifepacks={"kilima_in12_rebel": lp},
        )

        sim = SimulatorState()
        sim.outcomes = _init_outcomes(ws)
        sim.char_map = {"kive": "kilima_in12_rebel"}

        return ws, sim, lp

    def test_unlock_locked_slot(self) -> None:
        from gigagen.core.simulator import _unlock_lifepack_slot
        ws, sim, lp = self._build_sim_with_lifepack()

        _unlock_lifepack_slot(
            ws, sim, "kilima_in12_rebel",
            "octave_3_locations", "8_sexta_menor",
        )

        slot = lp.octave_3_locations.slots["8_sexta_menor"]
        assert slot.locked is False
        assert slot.unlocked is True

    def test_unlock_already_unlocked_is_noop(self) -> None:
        from gigagen.core.simulator import _unlock_lifepack_slot
        ws, sim, lp = self._build_sim_with_lifepack()

        # 0_tonica is already unlocked
        _unlock_lifepack_slot(
            ws, sim, "kilima_in12_rebel",
            "octave_3_locations", "0_tonica",
        )
        slot = lp.octave_3_locations.slots["0_tonica"]
        assert slot.locked is False  # still unlocked, no error

    def test_unlock_records_outcome(self) -> None:
        from gigagen.core.simulator import _unlock_lifepack_slot
        ws, sim, lp = self._build_sim_with_lifepack()

        _unlock_lifepack_slot(
            ws, sim, "kilima_in12_rebel",
            "octave_3_locations", "8_sexta_menor",
        )

        outcome = sim.outcomes["kilima_in12_rebel"]
        assert "unlocked" in outcome.bond_state
        assert "8_sexta_menor" in outcome.bond_state

    def test_unlock_via_event_rule(self) -> None:
        """Full integration: event rule with unlock_lifepack_slot."""
        import random
        from gigagen.core.simulator import _apply_rule
        ws, sim, lp = self._build_sim_with_lifepack()

        rule = {
            "event_id": "E_TEST",
            "unlock_lifepack_slot": [
                {
                    "character": "kive",
                    "octave": "octave_3_locations",
                    "slot_key": "8_sexta_menor",
                }
            ],
        }

        _apply_rule(rule, ws, sim, random.Random(1))

        slot = lp.octave_3_locations.slots["8_sexta_menor"]
        assert slot.locked is False
        assert slot.unlocked is True

    def test_unlock_missing_lifepack_is_noop(self) -> None:
        from gigagen.core.simulator import _unlock_lifepack_slot
        ws, sim, _ = self._build_sim_with_lifepack()

        # Try to unlock for a character that has no lifepack
        _unlock_lifepack_slot(
            ws, sim, "nonexistent",
            "octave_3_locations", "8_sexta_menor",
        )
        # No crash


# ---------------------------------------------------------------------------
# LP-6: Octave 8 — Invariants and variables
# ---------------------------------------------------------------------------


class TestOctave8Invariants:
    @staticmethod
    def _build_lp_with_events() -> LifePack:
        lp = build_empty_lifepack("D#", mode="minor")
        # Mark some slots as invariant/variable
        s0 = lp.octave_8_eventos.slots["0_tonica"]
        s0.event_type = "invariant"
        s0.entity_name = "Funeral"
        s0.locked = False

        s3 = lp.octave_8_eventos.slots["3_tercera_menor"]
        s3.event_type = "invariant"
        s3.entity_name = "War declared"

        s7 = lp.octave_8_eventos.slots["7_quinta_justa"]
        s7.event_type = "variable"
        s7.entity_name = ""
        return lp

    def test_invariants_pre_resolved(self) -> None:
        lp = self._build_lp_with_events()
        count = resolve_octave_8_invariants(lp)
        assert count == 2  # two invariant slots

        s0 = lp.octave_8_eventos.slots["0_tonica"]
        assert s0.resolved is True
        s3 = lp.octave_8_eventos.slots["3_tercera_menor"]
        assert s3.resolved is True

    def test_variables_not_resolved_by_invariants(self) -> None:
        lp = self._build_lp_with_events()
        resolve_octave_8_invariants(lp)
        s7 = lp.octave_8_eventos.slots["7_quinta_justa"]
        assert s7.resolved is False

    def test_resolve_variable(self) -> None:
        lp = self._build_lp_with_events()
        ok = resolve_octave_8_variable(lp, "VAR_DEV", "participates")
        assert ok is True
        s7 = lp.octave_8_eventos.slots["7_quinta_justa"]
        assert s7.resolved is True
        assert s7.entity_id == "VAR_DEV"
        assert s7.entity_name == "participates"

    def test_resolve_variable_no_slot_returns_false(self) -> None:
        lp = build_empty_lifepack("C")
        # No slots marked as variable
        ok = resolve_octave_8_variable(lp, "VAR_X", "yes")
        assert ok is False

    def test_already_resolved_invariant_is_noop(self) -> None:
        lp = self._build_lp_with_events()
        count1 = resolve_octave_8_invariants(lp)
        count2 = resolve_octave_8_invariants(lp)
        assert count1 == 2
        assert count2 == 0  # already resolved

    def test_kive_lifepack_has_invariant_slot(self) -> None:
        """Kive's lifepack loads with event_type field from JSON."""
        kive_path = DOCS_DIR / "kilima_in12_rebel_lifepack.json"
        if not kive_path.exists():
            pytest.skip("Kive lifepack not found")
        raw = json.loads(kive_path.read_text(encoding="utf-8"))
        lp = LifePack.model_validate(raw)
        s0 = lp.octave_8_eventos.slots["0_tonica"]
        assert s0.event_type == "invariant"

    def test_kive_invariants_resolve(self) -> None:
        """Post-resolve, Kive's invariant slots are resolved."""
        kive_path = DOCS_DIR / "kilima_in12_rebel_lifepack.json"
        if not kive_path.exists():
            pytest.skip("Kive lifepack not found")
        raw = json.loads(kive_path.read_text(encoding="utf-8"))
        lp = LifePack.model_validate(raw)
        count = resolve_octave_8_invariants(lp)
        assert count >= 1
        s0 = lp.octave_8_eventos.slots["0_tonica"]
        assert s0.resolved is True


# ---------------------------------------------------------------------------
# LP-7: TUI Life Pack Inspector
# ---------------------------------------------------------------------------


class TestLifePackInspectorScreen:
    def test_screen_builds_content_with_lifepack(self) -> None:
        from gigagen.core.entity import Character
        from gigagen.core.world_state import WorldState
        from gigagen.cli.tui.screens import LifePackInspectorScreen

        lp = build_empty_lifepack("D#", mode="minor")
        lp.meta.entity_id = "kilima_in12_rebel"
        lp.meta.entity_name = "Kive"
        lp.meta.collection = "kilima_in12"

        char = Character(
            id="kilima_in12_rebel",
            entity_type="character",
            name="Kive",
            canon_level="fixed",
            archetype="REB",
            note="D#",
            hero_type="tragic_hero",
            civil_name="Kive",
            role_name="The Rebel",
            status="active",
            current_location_id="loc.cave",
            emotional_load="neutral",
        )

        ws = WorldState(
            world_id="test",
            seed=1,
            phase="test",
            entities={"kilima_in12_rebel": char},
            lifepacks={"kilima_in12_rebel": lp},
        )

        screen = LifePackInspectorScreen("kilima_in12_rebel", ws)
        content = screen._build_content()

        assert "Kive" in content
        assert "D#" in content
        assert "Oct 7" in content
        assert "Oct 3" in content

    def test_screen_handles_no_lifepack(self) -> None:
        from gigagen.core.entity import Character
        from gigagen.core.world_state import WorldState
        from gigagen.cli.tui.screens import LifePackInspectorScreen

        char = Character(
            id="kilima_in12_orphan",
            entity_type="character",
            name="Len",
            canon_level="fixed",
            archetype="ORP",
            note="E",
            hero_type="mythological_hero",
            civil_name="Helena",
            role_name="The Orphan",
            status="transferred",
            current_location_id="loc.limbo",
            emotional_load="neutral",
        )

        ws = WorldState(
            world_id="test",
            seed=1,
            phase="test",
            entities={"kilima_in12_orphan": char},
        )

        screen = LifePackInspectorScreen("kilima_in12_orphan", ws)
        content = screen._build_content()
        assert "No Life Pack" in content

    def test_screen_shows_filled_slots_green(self) -> None:
        from gigagen.core.world_state import WorldState
        from gigagen.cli.tui.screens import LifePackInspectorScreen

        lp = build_empty_lifepack("D#", mode="minor")
        lp.meta.entity_id = "test"
        lp.meta.entity_name = "Test"
        lp.octave_7_personajes.slots["7_quinta_justa"].entity_name = "Cris"

        ws = WorldState(
            world_id="test", seed=1, phase="test",
            lifepacks={"test": lp},
        )

        screen = LifePackInspectorScreen("test", ws)
        content = screen._build_content()
        assert "[green]" in content
        assert "Cris" in content

    def test_screen_shows_locked_slots_dim(self) -> None:
        from gigagen.core.world_state import WorldState
        from gigagen.cli.tui.screens import LifePackInspectorScreen

        lp = build_empty_lifepack("C", mode="minor")
        lp.meta.entity_id = "test"
        lp.meta.entity_name = "Test"

        ws = WorldState(
            world_id="test", seed=1, phase="test",
            lifepacks={"test": lp},
        )

        screen = LifePackInspectorScreen("test", ws)
        content = screen._build_content()
        assert "[dim]" in content
        assert "(locked)" in content


# ---------------------------------------------------------------------------
# LP-8: Ánimas — Element-based slot computation
# ---------------------------------------------------------------------------


class TestElementCatalog:
    def test_load_catalog(self) -> None:
        catalog = load_elements_catalog()
        assert len(catalog) == 16

    def test_fundamental_elements(self) -> None:
        catalog = load_elements_catalog()
        fundamentals = [e for e in catalog if e.tier == "fundamental"]
        assert len(fundamentals) == 4

    def test_mixed_require_two(self) -> None:
        catalog = load_elements_catalog()
        for e in catalog:
            if e.tier == "mixed":
                assert len(e.requires) == 2

    def test_supreme_requires_all_four(self) -> None:
        catalog = load_elements_catalog()
        for e in catalog:
            if e.tier == "supreme":
                assert len(e.requires) == 4


class TestComputeAnimaSlots:
    @pytest.fixture
    def catalog(self) -> list:
        return load_elements_catalog()

    def test_kive_fire_dominated_earth_latent(self, catalog) -> None:
        """Kive: fuego dominado, tierra innata → 1 active, 1 available, metal future."""
        config = ElementConfig(
            innate_elements=["fuego", "tierra"],
            dominated_elements=["fuego"],
            latent_elements=["tierra"],
        )
        results = compute_available_anima_slots(config, catalog)
        active = [r for r in results if r.status == "active"]
        available = [r for r in results if r.status == "available"]
        future = [r for r in results if r.status == "future"]

        assert len(active) == 1
        assert active[0].element_id == "fuego"
        assert len(available) == 1
        assert available[0].element_id == "tierra"
        # Metal (fuego+tierra) should be future
        future_ids = {r.element_id for r in future}
        assert "metal" in future_ids

    def test_dev_no_elements(self, catalog) -> None:
        """Dev: no elements → 0 slots."""
        config = ElementConfig()
        results = compute_available_anima_slots(config, catalog)
        assert len(results) == 0

    def test_len_ether_maximum(self, catalog) -> None:
        """Len: all 4 fundamentals dominated → active + many futures."""
        config = ElementConfig(
            innate_elements=["agua", "fuego", "tierra", "aire"],
            dominated_elements=["agua", "fuego", "tierra", "aire"],
        )
        results = compute_available_anima_slots(config, catalog)
        active = [r for r in results if r.status == "active"]
        future = [r for r in results if r.status == "future"]

        assert len(active) == 4  # all fundamentals
        # All mixed, truncated, and supreme are unlockable
        assert len(future) >= 10  # 6 mixed + 4 truncated + 2 supreme = 12

    def test_single_element_no_fusions(self, catalog) -> None:
        """One element → 1 active, 0 fusions available."""
        config = ElementConfig(
            innate_elements=["agua"],
            dominated_elements=["agua"],
        )
        results = compute_available_anima_slots(config, catalog)
        assert len(results) == 1
        assert results[0].status == "active"

    def test_two_elements_unlock_fusion(self, catalog) -> None:
        """Agua + Aire innate → Nube is future."""
        config = ElementConfig(
            innate_elements=["agua", "aire"],
            dominated_elements=["agua"],
        )
        results = compute_available_anima_slots(config, catalog)
        future_ids = {r.element_id for r in results if r.status == "future"}
        assert "nube" in future_ids
